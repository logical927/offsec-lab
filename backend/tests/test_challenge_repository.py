import asyncio
from unittest.mock import AsyncMock, Mock

from app.repositories import ChallengeRepository


def test_get_active_filters_by_id_and_visibility() -> None:
    result = Mock()
    result.scalar_one_or_none.return_value = None
    session = Mock()
    session.execute = AsyncMock(return_value=result)
    repository = ChallengeRepository(session)

    assert asyncio.run(repository.get_active(42)) is None

    statement = session.execute.await_args.args[0]
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
    assert "challenges.id = 42" in sql
    assert "challenges.is_active IS true" in sql
