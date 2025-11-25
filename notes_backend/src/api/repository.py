import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import Note, NoteCreate, NoteUpdate


class InMemoryNotesRepository:
    """Thread-safe in-memory repository for notes.

    Stores notes in a dictionary keyed by auto-incrementing integer IDs.
    Provides CRUD operations and simple case-insensitive search over title and content.
    Results for list operations are ordered by updated_at descending.

    This repository is designed for easy swapping with a persistent implementation in the future.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._notes: Dict[int, Note] = {}
        self._next_id: int = 1

    def _now(self) -> datetime:
        """Return current UTC datetime for timestamps."""
        return datetime.now(timezone.utc)

    # PUBLIC_INTERFACE
    def list_notes(self, query: Optional[str] = None) -> List[Note]:
        """List all notes, optionally filtered by a case-insensitive query on title/content.

        Args:
            query: Optional search string. If provided, matches are case-insensitive
                   and will include any note whose title or content contains the query.

        Returns:
            A list of notes ordered by updated_at descending.
        """
        with self._lock:
            notes = list(self._notes.values())
            if query:
                q = query.lower()
                notes = [
                    n for n in notes
                    if q in n.title.lower() or q in n.content.lower()
                ]
            # Order by updated_at descending
            notes.sort(key=lambda n: n.updated_at, reverse=True)
            return list(notes)

    # PUBLIC_INTERFACE
    def get_note(self, id: int) -> Optional[Note]:
        """Retrieve a note by ID.

        Args:
            id: The note identifier.

        Returns:
            The note if found, else None.
        """
        with self._lock:
            return self._notes.get(id)

    # PUBLIC_INTERFACE
    def create_note(self, payload: NoteCreate) -> Note:
        """Create a new note.

        Args:
            payload: The data required to create a note.

        Returns:
            The created Note with assigned id and timestamps.
        """
        with self._lock:
            note_id = self._next_id
            self._next_id += 1
            now = self._now()
            note = Note(
                id=note_id,
                title=payload.title,
                content=payload.content,
                created_at=now,
                updated_at=now,
            )
            self._notes[note_id] = note
            return note

    # PUBLIC_INTERFACE
    def update_note(self, id: int, payload: NoteUpdate) -> Optional[Note]:
        """Update an existing note.

        Args:
            id: The note identifier.
            payload: Fields to update; only provided fields are updated.

        Returns:
            The updated Note if it exists, else None.
        """
        with self._lock:
            existing = self._notes.get(id)
            if not existing:
                return None
            updated_title = payload.title if payload.title is not None else existing.title
            updated_content = payload.content if payload.content is not None else existing.content
            updated_note = Note(
                id=existing.id,
                title=updated_title,
                content=updated_content,
                created_at=existing.created_at,
                updated_at=self._now(),
            )
            self._notes[id] = updated_note
            return updated_note

    # PUBLIC_INTERFACE
    def delete_note(self, id: int) -> bool:
        """Delete a note by ID.

        Args:
            id: The note identifier.

        Returns:
            True if a note was deleted, False if not found.
        """
        with self._lock:
            if id in self._notes:
                del self._notes[id]
                return True
            return False


# Singleton instance intended to be imported and reused by API routes.
# PUBLIC_INTERFACE
def get_repository() -> InMemoryNotesRepository:
    """Get the singleton in-memory notes repository instance."""
    global _REPO_SINGLETON
    try:
        return _REPO_SINGLETON
    except NameError:
        _REPO_SINGLETON = InMemoryNotesRepository()
        return _REPO_SINGLETON
