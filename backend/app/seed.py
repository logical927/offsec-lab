"""Run after `alembic upgrade head`: python -m app.seed.

Updates Mission 1 in place; never resets progress or replaces challenge IDs.
"""
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.database import DatabaseSettings
from app.models import Challenge, Hint, Mission
from app.mission01 import CHALLENGES, DESCRIPTION, LEARNING_EXPLANATION, TITLE


def seed_mission01(session: Session) -> None:
    # Serialize initialization with other seed runs on PostgreSQL.
    if session.bind.dialect.name == "postgresql":
        session.execute(text("SELECT pg_advisory_xact_lock(22001)"))
    mission = session.get(Mission, 1)
    if mission is None:
        mission = Mission(id=1, slug="m01-recon", sort_order=1)
        session.add(mission)
    mission.title = TITLE
    mission.description = DESCRIPTION
    mission.learning_explanation = LEARNING_EXPLANATION
    mission.is_active = True
    session.flush()

    existing = session.scalars(
        select(Challenge).where(Challenge.mission_id == 1).order_by(Challenge.sort_order)
    ).all()
    if any(c.sort_order not in range(1, 6) for c in existing):
        raise ValueError("Mission 1 has unexpected challenge orders; review before seeding.")
    by_order = {c.sort_order: c for c in existing}
    for order, (title, description, answer, hints) in enumerate(CHALLENGES, 1):
        challenge = by_order.get(order)
        if challenge is None:
            challenge = Challenge(mission_id=1, slug=title.lower().replace(" ", "-"), sort_order=order)
            session.add(challenge)
        challenge.title = title
        challenge.description = description
        challenge.accepted_answers = [answer]
        challenge.is_active = True
        session.flush()
        by_level = {hint.level: hint for hint in challenge.hints}
        for level, content in enumerate(hints, 1):
            hint = by_level.get(level)
            if hint is None:
                hint = Hint(challenge_id=challenge.id, level=level)
                challenge.hints.append(hint)
            hint.content = content

    # Mission 1's fixed registry ID must not leave the generated-ID sequence behind.
    if session.bind.dialect.name == "postgresql":
        session.execute(text("SELECT setval(pg_get_serial_sequence('missions', 'id'), (SELECT max(id) FROM missions))"))
    session.flush()


def main() -> None:
    engine = create_engine(DatabaseSettings.from_environment().sqlalchemy_url())
    try:
        with Session(engine) as session, session.begin():
            seed_mission01(session)
    finally:
        engine.dispose()
    print("Mission 01 content initialized; existing progress preserved.")


if __name__ == "__main__":
    main()
