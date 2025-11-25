from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base fields shared by Note models."""
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content/body of the note")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Payload model used to create a new note."""
    pass


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Payload model used to update an existing note (partial update)."""
    title: Optional[str] = Field(None, description="The updated title of the note")
    content: Optional[str] = Field(None, description="The updated content of the note")


# PUBLIC_INTERFACE
class Note(NoteBase):
    """Represents a persisted note entity."""
    id: int = Field(..., description="Unique identifier of the note")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
