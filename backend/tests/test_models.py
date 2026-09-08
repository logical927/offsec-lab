from sqlalchemy import CheckConstraint, UniqueConstraint

from app.models import Base, Challenge, Mission, Progress


def constraint_names(
    model: type[Mission] | type[Challenge] | type[Progress],
    kind: type,
) -> set[str]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind) and constraint.name is not None
    }


def unique_columns(
    model: type[Mission] | type[Challenge] | type[Progress],
) -> set[tuple[str, ...]]:
    return {
        tuple(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def test_model_metadata_contains_domain_tables() -> None:
    assert set(Base.metadata.tables) == {"missions", "challenges", "progress", "hints"}


def test_required_and_nullable_columns() -> None:
    for model in (Mission, Challenge):
        columns = model.__table__.columns
        assert columns["id"].primary_key
        assert columns["slug"].nullable is False
        assert columns["title"].nullable is False
        assert columns["description"].nullable is True
        assert columns["sort_order"].nullable is False
        assert columns["is_active"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["created_at"].type.timezone is True
        assert columns["updated_at"].nullable is False
        assert columns["updated_at"].type.timezone is True

    assert Challenge.__table__.columns["mission_id"].nullable is False
    assert Challenge.__table__.columns["accepted_answers"].nullable is True
    assert Progress.__table__.columns["mission_id"].nullable is False
    assert Progress.__table__.columns["challenge_id"].nullable is False
    assert Progress.__table__.columns["status"].nullable is False


def test_database_constraints_are_declared() -> None:
    assert "ck_missions_sort_order_positive" in constraint_names(
        Mission, CheckConstraint
    )
    assert "ck_challenges_sort_order_positive" in constraint_names(
        Challenge, CheckConstraint
    )
    assert unique_columns(Mission) == {("slug",)}
    assert unique_columns(Challenge) == {
        ("mission_id", "id"),
        ("mission_id", "slug"),
        ("mission_id", "sort_order"),
    }
    assert constraint_names(Mission, UniqueConstraint) == {"uq_missions_slug"}
    assert {
        "uq_challenges_mission_id_id",
        "uq_challenges_mission_id_slug",
        "uq_challenges_mission_id_sort_order",
    } == constraint_names(Challenge, UniqueConstraint)
    assert unique_columns(Progress) == {("mission_id", "challenge_id")}
    assert "ck_progress_status" in constraint_names(Progress, CheckConstraint)


def test_mission_challenge_relationship_uses_restrict_without_delete_cascade() -> None:
    foreign_key = next(iter(Challenge.__table__.columns["mission_id"].foreign_keys))
    assert foreign_key.target_fullname == "missions.id"
    assert foreign_key.ondelete == "RESTRICT"

    assert Mission.challenges.property.back_populates == "mission"
    assert Challenge.mission.property.back_populates == "challenges"
    assert "delete" not in Mission.challenges.property.cascade
    assert Mission.challenges.property.passive_deletes == "all"


def test_progress_uses_composite_challenge_foreign_key() -> None:
    foreign_key = next(
        constraint
        for constraint in Progress.__table__.foreign_key_constraints
        if constraint.name == "fk_progress_mission_challenge"
    )
    assert tuple(column.name for column in foreign_key.columns) == (
        "mission_id",
        "challenge_id",
    )
    assert tuple(element.target_fullname for element in foreign_key.elements) == (
        "challenges.mission_id",
        "challenges.id",
    )
    assert foreign_key.ondelete == "RESTRICT"
