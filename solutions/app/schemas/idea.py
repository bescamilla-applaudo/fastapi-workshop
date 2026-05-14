from datetime import datetime

from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: str = Field(default="general", max_length=50)
    is_public: bool = False


class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=50)
    is_public: bool | None = None


class IdeaResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int

    model_config = {"from_attributes": True}
