from pydantic import BaseModel

from app.services import ChallengeProgressStatus, MissionProgressStatus


class ChallengeProgressResponse(BaseModel):
    challenge_id: int
    status: ChallengeProgressStatus


class MissionProgressResponse(BaseModel):
    mission_id: int
    status: MissionProgressStatus
    challenges: list[ChallengeProgressResponse]


class ProgressResponse(BaseModel):
    missions: list[MissionProgressResponse]
