import logging
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from app.models import Challenge, Mission, Progress
from app.repositories import (
    ChallengeRepository,
    MissionRepository,
    ProgressRepository,
)

logger = logging.getLogger(__name__)


class ChallengeProgressStatus(StrEnum):
    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    COMPLETED = "COMPLETED"


class MissionProgressStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ChallengeLockedError(Exception):
    pass


@dataclass(frozen=True)
class ChallengeProgressSnapshot:
    challenge_id: int
    status: ChallengeProgressStatus


@dataclass(frozen=True)
class MissionProgressSnapshot:
    mission_id: int
    status: MissionProgressStatus
    challenges: Sequence[ChallengeProgressSnapshot]


@dataclass(frozen=True)
class ProgressTransition:
    challenge_status: ChallengeProgressStatus
    next_challenge_id: int | None
    mission_status: MissionProgressStatus


def build_mission_snapshot(
    mission_id: int,
    challenges: Sequence[Challenge],
    progress_rows: Sequence[Progress],
) -> MissionProgressSnapshot:
    active_challenge_ids = {challenge.id for challenge in challenges}
    completed_ids = {
        row.challenge_id
        for row in progress_rows
        if row.challenge_id in active_challenge_ids
        and row.status == ChallengeProgressStatus.COMPLETED
    }
    challenge_snapshots: list[ChallengeProgressSnapshot] = []
    previous_are_completed = True

    for challenge in challenges:
        if challenge.id in completed_ids:
            status = ChallengeProgressStatus.COMPLETED
        elif previous_are_completed:
            status = ChallengeProgressStatus.AVAILABLE
        else:
            status = ChallengeProgressStatus.LOCKED

        challenge_snapshots.append(
            ChallengeProgressSnapshot(challenge_id=challenge.id, status=status)
        )
        previous_are_completed = previous_are_completed and (
            status == ChallengeProgressStatus.COMPLETED
        )

    if challenge_snapshots and all(
        item.status == ChallengeProgressStatus.COMPLETED
        for item in challenge_snapshots
    ):
        mission_status = MissionProgressStatus.COMPLETED
    elif completed_ids:
        mission_status = MissionProgressStatus.IN_PROGRESS
    else:
        mission_status = MissionProgressStatus.NOT_STARTED

    return MissionProgressSnapshot(
        mission_id=mission_id,
        status=mission_status,
        challenges=challenge_snapshots,
    )


class ProgressService:
    def __init__(
        self,
        mission_repository: MissionRepository,
        challenge_repository: ChallengeRepository,
        progress_repository: ProgressRepository,
    ) -> None:
        self._mission_repository = mission_repository
        self._challenge_repository = challenge_repository
        self._progress_repository = progress_repository

    async def list_progress(self) -> Sequence[MissionProgressSnapshot]:
        snapshots: list[MissionProgressSnapshot] = []
        for mission in await self._mission_repository.list_active():
            challenges = await self._challenge_repository.list_active_for_mission(
                mission.id
            )
            progress_rows = await self._progress_repository.list_for_mission(
                mission.id
            )
            snapshots.append(
                build_mission_snapshot(mission.id, challenges, progress_rows)
            )
        return snapshots

    async def record_answer(
        self,
        mission: Mission,
        challenge: Challenge,
        correct: bool,
    ) -> ProgressTransition:
        await self._progress_repository.lock_mission(mission.id)
        challenges = await self._challenge_repository.list_active_for_mission(
            mission.id
        )
        progress_rows = list(
            await self._progress_repository.list_for_mission(mission.id)
        )
        snapshot = build_mission_snapshot(mission.id, challenges, progress_rows)
        snapshot_by_id = {
            item.challenge_id: item for item in snapshot.challenges
        }
        current = snapshot_by_id[challenge.id]
        if current.status == ChallengeProgressStatus.LOCKED:
            await self._progress_repository.rollback()
            raise ChallengeLockedError

        rows_by_challenge_id = {row.challenge_id: row for row in progress_rows}
        new_rows: list[Progress] = []
        for item in snapshot.challenges:
            if item.challenge_id not in rows_by_challenge_id:
                row = Progress(
                    mission_id=mission.id,
                    challenge_id=item.challenge_id,
                    status=item.status,
                )
                rows_by_challenge_id[item.challenge_id] = row
                new_rows.append(row)
        if new_rows:
            self._progress_repository.add_all(new_rows)

        was_completed = current.status == ChallengeProgressStatus.COMPLETED
        mission_was_completed = snapshot.status == MissionProgressStatus.COMPLETED
        if correct:
            rows_by_challenge_id[challenge.id].status = (
                ChallengeProgressStatus.COMPLETED
            )

        try:
            await self._progress_repository.flush()
            updated_snapshot = build_mission_snapshot(
                mission.id,
                challenges,
                list(rows_by_challenge_id.values()),
            )
            updated_by_id = {
                item.challenge_id: item for item in updated_snapshot.challenges
            }
            for item in updated_snapshot.challenges:
                rows_by_challenge_id[item.challenge_id].status = item.status
            await self._progress_repository.commit()
        except Exception:
            await self._progress_repository.rollback()
            raise

        next_challenge_id = next(
            (
                item.challenge_id
                for item in updated_snapshot.challenges
                if item.status == ChallengeProgressStatus.AVAILABLE
                and item.challenge_id != challenge.id
            ),
            None,
        )

        if correct and not was_completed:
            logger.info(
                "event=CHALLENGE_COMPLETED mission_id=%s challenge_id=%s",
                mission.id,
                challenge.id,
            )
            if (
                updated_snapshot.status == MissionProgressStatus.COMPLETED
                and not mission_was_completed
            ):
                logger.info("event=MISSION_COMPLETED mission_id=%s", mission.id)

        return ProgressTransition(
            challenge_status=updated_by_id[challenge.id].status,
            next_challenge_id=next_challenge_id,
            mission_status=updated_snapshot.status,
        )

    async def assert_unlocked(
        self,
        mission: Mission,
        challenge: Challenge,
    ) -> None:
        await self._progress_repository.lock_mission(mission.id)
        challenges = await self._challenge_repository.list_active_for_mission(
            mission.id
        )
        progress_rows = await self._progress_repository.list_for_mission(mission.id)
        snapshot = build_mission_snapshot(mission.id, challenges, progress_rows)
        current = next(
            item for item in snapshot.challenges if item.challenge_id == challenge.id
        )
        if current.status == ChallengeProgressStatus.LOCKED:
            await self._progress_repository.rollback()
            raise ChallengeLockedError
