from typing import Literal

from pydantic import BaseModel


class LabStartResponse(BaseModel):
    mission_id: int
    status: Literal["running"]
    already_running: bool
