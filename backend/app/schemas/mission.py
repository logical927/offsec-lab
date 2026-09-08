from pydantic import BaseModel, ConfigDict, Field


class HintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level: int
    content: str


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
    hints: list[HintResponse] = Field(default_factory=list)


class MissionDetailResponse(MissionSummaryResponse):
    challenges: list[ChallengeSummaryResponse]
    learning_explanation: str | None = None
