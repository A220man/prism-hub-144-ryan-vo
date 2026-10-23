# Prompt Schemas
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PromptBase(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=255)
    prompt_text: str = Field(..., min_length=1)
    is_default: bool = False
    tags: str = ""


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    model_name: Optional[str] = Field(None, min_length=1, max_length=255)
    prompt_text: Optional[str] = Field(None, min_length=1)
    is_default: Optional[bool] = None
    tags: Optional[str] = None


class PromptResponse(PromptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptListResponse(BaseModel):
    items: list[PromptResponse]
    total: int
    page: int
    page_size: int
    total_pages: int