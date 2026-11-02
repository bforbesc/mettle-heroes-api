from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator

PlanName = Literal["Pro", "Max", "Enterprise"]


class ClientIn(BaseModel):
    name: str
    plan: PlanName
    seats: int
    contact_email: str | None = None


class TierChange(BaseModel):
    plan: PlanName


class Window(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def naive_and_end_after_start(self):
        if self.start.tzinfo is not None or self.end.tzinfo is not None:
            raise ValueError("start and end must not carry a time zone")
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class BookingIn(BaseModel):
    client_id: int
    hero: str
    mission: str
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
