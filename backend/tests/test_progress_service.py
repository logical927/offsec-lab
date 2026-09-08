import asyncio
import logging
from collections.abc import Sequence
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Challenge, Mission, Progress
from app.services import (
    ChallengeLockedError,
    ChallengeProgressStatus,
    MissionProgressStatus,
    ProgressService,
)
from app.services.progress_service import build_mission_snapshot


def mission() -> Mission:
    return Mission(id=1, slug="m01", title="Recon", sort_order=1, is_active=True)


def challenges(count: int = 3) -> list[Challenge]:
    return [
        Challenge(
            id=index,
            mission_id=1,
            slug=f"c{index}",
            title=f"Challenge {index}",
            sort_order=index,
            is_active=True,
        )
        for index in range(1, count + 1)
    ]


def progress_row(challenge_id: int, status: str) -> Progress:
    return Progress(
        id=challenge_id,
        mission_id=1,
        challenge_id=challenge_id,
        status=status,
    )


@pytest.mark.parametrize(
    ("rows", "expected_statuses", "mission_status"),
    [
        (
            [],
            ["AVAILABLE", "LOCKED", "LOCKED"],
            MissionProgressStatus.NOT_STARTED,
        ),
        (
            [progress_row(1, "COMPLETED")],
            ["COMPLETED", "AVAILABLE", "LOCKED"],
            MissionProgressStatus.IN_PROGRESS,
        ),
        (
            [
                progress_row(1, "COMPLETED"),
                progress_row(2, "COMPLETED"),
                progress_row(3, "COMPLETED"),
            ],
            ["COMPLETED", "COMPLETED", "COMPLETED"],
            MissionProgressStatus.COMPLETED,
        ),
    ],
)
def test_build_mission_snapshot_derives_sequential_state(
    rows: Sequence[Progress],
    expected_statuses: list[str],
    mission_status: MissionProgressStatus,
) -> None:
    snapshot = build_mission_snapshot(1, challenges(), rows)

    assert [item.status for item in snapshot.challenges] == expected_statuses
    assert snapshot.status == mission_status


def test_inactive_challenge_progress_does_not_change_mission_status() -> None:
    snapshot = build_mission_snapshot(
        1,
        [],
        [progress_row(99, "COMPLETED")],
    )

    assert snapshot.status == MissionProgressStatus.NOT_STARTED


class FakeProgressRepository:
    def __init__(self, rows: Sequence[Progress] = ()) -> None:
        self.rows = list(rows)
        self.locked_mission_ids: list[int] = []
        self.commits = 0
        self.rollbacks = 0
        self.flushes = 0

    async def lock_mission(self, mission_id: int) -> None:
        self.locked_mission_ids.append(mission_id)

    async def list_for_mission(self, mission_id: int) -> Sequence[Progress]:
        return [row for row in self.rows if row.mission_id == mission_id]

    def add_all(self, rows: Sequence[Progress]) -> None:
        self.rows.extend(rows)

    async def flush(self) -> None:
        self.flushes += 1

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


def progress_service(
    rows: Sequence[Progress] = (),
) -> tuple[ProgressService, FakeProgressRepository]:
    mission_repository = Mock()
    mission_repository.list_active = AsyncMock(return_value=[mission()])
    challenge_repository = Mock()
    challenge_repository.list_active_for_mission = AsyncMock(
        return_value=challenges()
    )
    progress_repository = FakeProgressRepository(rows)
    service = ProgressService(
        mission_repository,
        challenge_repository,
        progress_repository,
    )
    return service, progress_repository


def test_list_progress_returns_derived_snapshot_without_writing() -> None:
    service, repository = progress_service()

    snapshots = asyncio.run(service.list_progress())

    assert snapshots[0].status == MissionProgressStatus.NOT_STARTED
    assert [item.status for item in snapshots[0].challenges] == [
        ChallengeProgressStatus.AVAILABLE,
        ChallengeProgressStatus.LOCKED,
        ChallengeProgressStatus.LOCKED,
    ]
    assert repository.rows == []
    assert repository.commits == 0


def test_correct_answer_completes_current_and_unlocks_next() -> None:
    service, repository = progress_service()
    current_mission = mission()
    current_challenge = challenges()[0]

    transition = asyncio.run(
        service.record_answer(current_mission, current_challenge, True)
    )

    assert transition.challenge_status == ChallengeProgressStatus.COMPLETED
    assert transition.next_challenge_id == 2
    assert transition.mission_status == MissionProgressStatus.IN_PROGRESS
    assert [row.status for row in repository.rows] == [
        ChallengeProgressStatus.COMPLETED,
        ChallengeProgressStatus.AVAILABLE,
        ChallengeProgressStatus.LOCKED,
    ]
    assert repository.locked_mission_ids == [1]
    assert repository.commits == 1


def test_incorrect_answer_keeps_current_available() -> None:
    service, repository = progress_service()

    transition = asyncio.run(
        service.record_answer(mission(), challenges()[0], False)
    )

    assert transition.challenge_status == ChallengeProgressStatus.AVAILABLE
    assert transition.next_challenge_id is None
    assert transition.mission_status == MissionProgressStatus.NOT_STARTED
    assert repository.commits == 1


def test_locked_challenge_is_rejected_without_persisting() -> None:
    service, repository = progress_service()

    with pytest.raises(ChallengeLockedError):
        asyncio.run(service.record_answer(mission(), challenges()[1], True))

    assert repository.rows == []
    assert repository.commits == 0
    assert repository.rollbacks == 1


def test_final_answer_completes_mission_and_logs_transitions(
    caplog: pytest.LogCaptureFixture,
) -> None:
    service, repository = progress_service(
        [
            progress_row(1, "COMPLETED"),
            progress_row(2, "COMPLETED"),
            progress_row(3, "AVAILABLE"),
        ]
    )

    with caplog.at_level(logging.INFO):
        transition = asyncio.run(
            service.record_answer(mission(), challenges()[2], True)
        )

    assert transition.mission_status == MissionProgressStatus.COMPLETED
    assert transition.next_challenge_id is None
    assert "event=CHALLENGE_COMPLETED" in caplog.text
    assert "event=MISSION_COMPLETED" in caplog.text
    assert repository.commits == 1


def test_assert_unlocked_rejects_before_answer_evaluation() -> None:
    service, repository = progress_service()

    with pytest.raises(ChallengeLockedError):
        asyncio.run(service.assert_unlocked(mission(), challenges()[1]))

    assert repository.rollbacks == 1


def test_database_failure_rolls_back_progress_changes() -> None:
    service, repository = progress_service()

    async def fail_flush() -> None:
        raise RuntimeError("database unavailable")

    repository.flush = fail_flush  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="database unavailable"):
        asyncio.run(service.record_answer(mission(), challenges()[0], True))

    assert repository.commits == 0
    assert repository.rollbacks == 1


@pytest.mark.parametrize("correct", [True, False])
def test_reanswer_preserves_completion_without_duplicate_rows_or_events(correct, caplog):
    service, repository = progress_service([
        progress_row(1, "COMPLETED"),
        progress_row(2, "COMPLETED"),
        progress_row(3, "COMPLETED"),
    ])
    original_rows = list(repository.rows)
    with caplog.at_level(logging.INFO):
        for _ in range(2):
            result = asyncio.run(service.record_answer(mission(), challenges()[2], correct))
            assert result.mission_status == MissionProgressStatus.COMPLETED
            assert result.challenge_status == ChallengeProgressStatus.COMPLETED
            assert result.next_challenge_id is None
    assert repository.rows == original_rows
    assert all(row.status == "COMPLETED" for row in repository.rows)
    assert "event=CHALLENGE_COMPLETED" not in caplog.text
    assert "event=MISSION_COMPLETED" not in caplog.text
