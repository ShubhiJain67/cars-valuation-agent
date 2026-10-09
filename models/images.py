from typing import Literal

from pydantic import BaseModel, Field

from constants.car import SEVERITIES
from constants.parts import PARTS

PartKey = Literal[tuple(PARTS)]
Severity = Literal[SEVERITIES]


class NumberCheck(BaseModel):
    number_visible: bool = Field(description="True only if a full vehicle registration number is clearly readable")
    shown_on: Literal["number_plate", "paper", "none"] = Field(description="Where the number is shown")
    registration_number: str | None = Field(description="The number exactly as written, or null if not readable")
    reason: str = Field(description="One short sentence explaining the decision")


class DetectedDamage(BaseModel):
    part: PartKey
    severity: Severity
    description: str = Field(description="What is wrong, in a few words, e.g. 'deep dent above wheel arch'")
    image_numbers: list[int] = Field(description="1-based numbers of the images where this damage is visible")
    confidence: float = Field(description="0 to 1: how sure you are this damage is real and correctly located")


class DamageReport(BaseModel):
    damages: list[DetectedDamage]
    unclear_areas: list[str] = Field(description="Parts or areas that could not be judged from these photos")
