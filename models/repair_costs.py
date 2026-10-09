from pydantic import BaseModel


class Costs(BaseModel):
    severity_1: int
    severity_2: int
    severity_3: int


class BySize(BaseModel):
    hatchback: Costs
    sedan: Costs
    suv: Costs


class RepairCosts(BaseModel):
    normal: BySize
    luxury: BySize
    