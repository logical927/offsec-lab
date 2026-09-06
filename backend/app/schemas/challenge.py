from typing import Annotated

from pydantic import BaseModel, StringConstraints

AnswerText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class ChallengeAnswerRequest(BaseModel):
    answer: AnswerText


class ChallengeAnswerResponse(BaseModel):
    correct: bool
