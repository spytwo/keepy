from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    content: str = Field(min_length=1)


class EntryRead(BaseModel):
    id: int
    title: str | None = None
    content: str

    model_config = ConfigDict(from_attributes=True)
