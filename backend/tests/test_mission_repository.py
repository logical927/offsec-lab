import asyncio
from unittest.mock import AsyncMock, Mock

from app.repositories import MissionRepository


def query_text(statement: object) -> str:
    return str(statement.compile(compile_kwargs={"literal_binds": True}))


def test_list_active_filters_and_orders_missions() -> None:
    result = Mock()
    result.scalars.return_value.all.return_value = []
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = MissionRepository(session)

    assert asyncio.run(repository.list_active()) == []

    statement = session.execute.await_args.args[0]
    sql = query_text(statement)
    assert "missions.is_active IS true" in sql
    assert "ORDER BY missions.sort_order, missions.id" in sql


def test_get_active_filters_by_id_and_visibility() -> None:
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = MissionRepository(session)

    assert asyncio.run(repository.get_active(42)) is None

    statement = session.execute.await_args.args[0]
    sql = query_text(statement)
    assert "missions.id = 42" in sql
    assert "missions.is_active IS true" in sql


def test_list_active_challenges_filters_and_orders_results() -> None:
    result = Mock()
    result.scalars.return_value.all.return_value = []
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = MissionRepository(session)

    assert asyncio.run(repository.list_active_challenges(7)) == []

    statement = session.execute.await_args.args[0]
    sql = query_text(statement)
    assert "challenges.mission_id = 7" in sql
    assert "challenges.is_active IS true" in sql
    assert "ORDER BY challenges.sort_order, challenges.id" in sql
