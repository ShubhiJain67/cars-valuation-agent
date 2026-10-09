from pydantic import BaseModel, Field


class CarFacts(BaseModel):
    is_real_model: bool
    first_year: int | None = Field(description="Year first sold in India")
    last_year: int | None = Field(description="Last year sold new in India; null if it is being still sold")
    ex_showroom_min: int | None = Field(description="Cheapest variant in rupees")
    ex_showroom_max: int | None = Field(description="Most expensive variant in rupees")
    sources: list | None = Field(description="List of links from where thi information was fetched")
