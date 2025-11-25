from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware

from .models import Note, NoteCreate, NoteUpdate
from .repository import get_repository

openapi_tags = [
    {
        "name": "health",
        "description": "Service health and meta endpoints",
    },
    {
        "name": "notes",
        "description": "Operations for managing notes",
    },
]

app = FastAPI(
    title="Notes Backend API",
    description="API for managing notes with CRUD and search.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Initialize singleton repository (for future endpoint use)
repo = get_repository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint for the Notes API.

    Returns:
        A JSON object indicating service health.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=List[Note],
    tags=["notes"],
    summary="List notes",
    description="List all notes, optionally filtered by a case-insensitive query over title and content.",
)
def list_notes(query: Optional[str] = Query(default=None, description="Optional search query")) -> List[Note]:
    """List notes with optional search.

    Args:
        query: Optional case-insensitive search string applied to title and content.

    Returns:
        List of notes ordered by updated_at descending.
    """
    return repo.list_notes(query=query)


# PUBLIC_INTERFACE
@app.get(
    "/notes/{id}",
    response_model=Note,
    tags=["notes"],
    summary="Get note by ID",
    description="Retrieve a single note by its ID.",
)
def get_note(id: int = Path(..., description="The ID of the note to retrieve")) -> Note:
    """Get a note by ID.

    Args:
        id: Identifier of the note.

    Returns:
        The requested note.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    note = repo.get_note(id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create a new note",
    description="Create a new note with title and content.",
)
def create_note(payload: NoteCreate) -> Note:
    """Create a new note.

    Args:
        payload: NoteCreate model containing title and content.

    Returns:
        The created note with ID and timestamps.
    """
    return repo.create_note(payload)


# PUBLIC_INTERFACE
@app.put(
    "/notes/{id}",
    response_model=Note,
    tags=["notes"],
    summary="Update a note",
    description="Update an existing note. Only provided fields will be updated.",
)
def update_note(
    id: int = Path(..., description="The ID of the note to update"),
    payload: NoteUpdate = ...,
) -> Note:
    """Update an existing note.

    Args:
        id: Identifier of the note to update.
        payload: Fields to update (title and/or content).

    Returns:
        The updated note.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    updated = repo.update_note(id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete a note",
    description="Delete a note by its ID.",
    responses={
        204: {"description": "Note deleted successfully"},
        404: {"description": "Note not found"},
    },
)
def delete_note(id: int = Path(..., description="The ID of the note to delete")) -> None:
    """Delete a note by ID.

    Args:
        id: Identifier of the note to delete.

    Returns:
        None. Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    deleted = repo.delete_note(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    # FastAPI will return 204 with no content by virtue of status_code above.
    return None
