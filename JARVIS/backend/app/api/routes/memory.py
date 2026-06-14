from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ...db.database import get_db
from ...models.note import Note

router = APIRouter(prefix="/memory", tags=["memory"])


class NoteCreate(BaseModel):
    """Request para crear un nuevo apunte."""
    title: str
    content: str
    tags: Optional[str] = ""


class NoteResponse(BaseModel):
    """Respuesta con información de un apunte."""
    id: int
    title: str
    content: str
    tags: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Guarda un nuevo apunte en la base de datos."""
    db_note = Note(
        title=note.title,
        content=note.content,
        tags=note.tags or ""
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/notes", response_model=List[NoteResponse])
async def list_notes(
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los apuntes o busca por título/tags.

    Args:
        limit: Máximo número de resultados
        search: Término de búsqueda (busca en título y tags)
    """
    query = db.query(Note)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Note.title.ilike(search_term)) |
            (Note.tags.ilike(search_term))
        )

    notes = query.order_by(Note.created_at.desc()).limit(limit).all()
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Obtiene un apunte específico por su ID."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Apunte no encontrado")
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteCreate,
    db: Session = Depends(get_db)
):
    """Actualiza un apunte existente."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Apunte no encontrado")

    note.title = note_update.title
    note.content = note_update.content
    note.tags = note_update.tags or ""

    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Elimina un apunte."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Apunte no encontrado")

    db.delete(note)
    db.commit()
    return {"message": "Apunte eliminado correctamente"}
