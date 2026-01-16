from pydantic import BaseModel, Field
from typing import List


class CreateProjectIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)


class CreateChatIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=80)


class SendMessageIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)


class CreateContextIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=4000)


class ToggleProjectContextIn(BaseModel):
    context_id: int
    is_active: bool


class CreateGroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)


class SetGroupItemsIn(BaseModel):
    context_ids: List[int] = Field(default_factory=list)


class ApplyGroupToProjectIn(BaseModel):
    group_id: int
    is_active: bool  # si true => activar todos; si false => desactivar todos
