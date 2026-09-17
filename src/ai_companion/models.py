from typing import List, Optional

from pydantic import BaseModel, Field


class Turn(BaseModel):
    role: str
    content: str


class UserProfile(BaseModel):
    name: Optional[str] = None
    likes: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
