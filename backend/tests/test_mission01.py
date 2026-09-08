"""Content persistence tests; PostgreSQL/API integration is explicitly opt-in."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Challenge, Hint, Mission, Progress
from app.mission01 import CHALLENGES
from app.seed import seed_mission01
from app.services.challenge_service import normalize_answer


def test_clean_seed_is_repeatable_and_preserves_identifiers_and_progress():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_mission01(session)
        session.commit()
        mission = session.get(Mission, 1)
        mission.slug = "existing-mission-slug"
        challenges = session.scalars(select(Challenge).order_by(Challenge.sort_order)).all()
        ids = [c.id for c in challenges]
        hint_ids = list(session.scalars(select(Hint.id).order_by(Hint.id)))
        session.add(Progress(mission_id=1, challenge_id=ids[0], status="COMPLETED"))
        session.commit()
        seed_mission01(session)
        seed_mission01(session)
        session.commit()
        assert len(session.scalars(select(Mission)).all()) == 1
        assert mission.slug == "existing-mission-slug"
        assert [c.id for c in session.scalars(select(Challenge).order_by(Challenge.sort_order))] == ids
        assert list(session.scalars(select(Hint.id).order_by(Hint.id))) == hint_ids
        assert len(hint_ids) == 15
        assert session.scalar(select(Progress.status)) == "COMPLETED"
        assert [c.sort_order for c in challenges] == [1, 2, 3, 4, 5]
        for challenge, content in zip(challenges, CHALLENGES, strict=True):
            assert [h.level for h in challenge.hints] == [1, 2, 3]
            assert challenge.accepted_answers == [content[2]]
    engine.dispose()


def test_public_content_never_contains_canonical_answers():
    from app.mission01 import DESCRIPTION, LEARNING_EXPLANATION, TITLE

    public = " ".join([TITLE, DESCRIPTION, LEARNING_EXPLANATION] + [
        value for title, task, _, hints in CHALLENGES for value in [title, task, *hints]
    ])
    for _, _, answer, _ in CHALLENGES:
        # Command port lists are investigation parameters, not an answer key.
        if answer != "22,80":
            assert normalize_answer(answer) not in normalize_answer(public)


@pytest.mark.parametrize("level", [0, 4, 1])
def test_hint_constraints_reject_invalid_or_duplicate_levels(level):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_mission01(session)
        session.commit()
        challenge_id = session.scalar(select(Challenge.id))
        session.add(Hint(challenge_id=challenge_id, level=level, content="Invalid hint"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert len(session.scalars(select(Hint)).all()) == 15
    engine.dispose()


def test_seed_refuses_unexpected_challenges_without_deleting_history():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_mission01(session)
        session.add(Challenge(mission_id=1, slug="unexpected", title="Existing", sort_order=6))
        session.commit()
        with pytest.raises(ValueError, match="unexpected challenge orders"):
            with session.begin():
                seed_mission01(session)
        assert len(session.scalars(select(Challenge)).all()) == 6
    engine.dispose()


@pytest.mark.skipif(os.getenv("OFFSEC_TEST_POSTGRES") != "1", reason="requires isolated PostgreSQL test schema")
def test_postgres_migration_seed_and_five_challenge_api_flow(monkeypatch):
    from alembic import command
    from alembic.config import Config
    from fastapi.testclient import TestClient
    from app.database import DatabaseSettings, _session_factory
    from app.main import app

    engine = create_engine(DatabaseSettings.from_environment().sqlalchemy_url())
    schema = "issue022_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    monkeypatch.setenv("PGOPTIONS", f"-csearch_path={schema}")
    isolated = create_engine(DatabaseSettings.from_environment().sqlalchemy_url())
    # Keep Alembic's fileConfig from disabling application/pytest loggers.
    config = Config()
    config.set_main_option("script_location", "alembic")
    try:
        command.upgrade(config, "head")
        command.check(config)
        with Session(isolated) as session, session.begin():
            seed_mission01(session)
        _session_factory.cache_clear()
        with TestClient(app) as client:
            listing = client.get("/api/v1/missions")
            detail = client.get("/api/v1/missions/1")
            assert listing.status_code == detail.status_code == 200
            assert len(listing.json()) == 1
            data = detail.json()
            assert data["learning_explanation"]
            challenges = data["challenges"]
            assert [c["sort_order"] for c in challenges] == [1, 2, 3, 4, 5]
            assert all([h["level"] for h in c["hints"]] == [1, 2, 3] for c in challenges)
            assert "accepted_answers" not in listing.text + detail.text
            for answer in ("ssh,http", "OpenSSH 9.2p1", "Northbridge Systems Status Portal"):
                assert answer not in listing.text + detail.text
            locked = client.post(f"/api/v1/challenges/{challenges[-1]['id']}/answers", json={"answer": CHALLENGES[-1][2]})
            assert locked.status_code == 409
            for index, challenge in enumerate(challenges):
                endpoint = f"/api/v1/challenges/{challenge['id']}/answers"
                before = client.get("/api/v1/progress").json()
                wrong = client.post(endpoint, json={"answer": "incorrect-observation"})
                assert wrong.status_code == 200
                assert wrong.json()["correct"] is False
                assert wrong.json()["status"] == "AVAILABLE"
                assert client.get("/api/v1/progress").json() == before
                answer = CHALLENGES[index][2]
                correct = client.post(endpoint, json={"answer": f"  {answer.upper()}  "})
                assert correct.status_code == 200
                assert correct.json()["correct"] is True
                assert correct.json()["status"] == "COMPLETED"
                assert correct.json()["next_challenge_id"] == (challenges[index + 1]["id"] if index < 4 else None)
                snapshot = client.get("/api/v1/progress").json()["missions"][0]
                assert [c["status"] for c in snapshot["challenges"]] == [
                    "COMPLETED" if i <= index else "AVAILABLE" if i == index + 1 else "LOCKED"
                    for i in range(5)
                ]
            assert snapshot["status"] == "COMPLETED"
            with Session(isolated) as session, session.begin():
                seed_mission01(session)
            assert client.get("/api/v1/progress").json()["missions"][0] == snapshot
        command.downgrade(config, "20260906_0003")
        command.upgrade(config, "head")
        with Session(isolated) as session, session.begin():
            seed_mission01(session)
            assert len(session.scalars(select(Hint)).all()) == 15
            assert all(p.status == "COMPLETED" for p in session.scalars(select(Progress)))
    finally:
        isolated.dispose()
        _session_factory.cache_clear()
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()
