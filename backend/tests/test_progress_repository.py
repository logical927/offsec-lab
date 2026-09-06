import asyncio
from unittest.mock import AsyncMock, Mock

from app.repositories import ProgressRepository


def test_list_for_mission_filters_by_mission_id() -> None:
    result = Mock()
    result.scalars.return_value.all.return_value = []
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = ProgressRepository(session)

    assert asyncio.run(repository.list_for_mission(7)) == []

    statement = session.execute.await_args.args[0]
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
    assert "progress.mission_id = 7" in sql


def test_lock_mission_uses_row_lock() -> None:
    result = Mock()
    result.scalar_one.return_value = 7
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = ProgressRepository(session)

    asyncio.run(repository.lock_mission(7))

    statement = session.execute.await_args.args[0]
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
    assert "missions.id = 7" in sql
    assert "FOR UPDATE" in sql
