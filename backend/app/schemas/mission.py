from pydantic import BaseModel, ConfigDict


class MissionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str | None
    sort_order: int


class ChallengeSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str | None
    sort_order: int


class MissionDetailResponse(MissionSummaryResponse):
    challenges: list[ChallengeSummaryResponse]
