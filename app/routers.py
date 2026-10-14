from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Entry
from app.schemas import EntryCreate, EntryRead

router = APIRouter(prefix="/entries", tags=["Entries"])


@router.post(
    "",
    response_model=EntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db),
):
    db_entry = Entry(content=entry.content)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("", response_model=list[EntryRead])
def get_entries(db: Session = Depends(get_db)):
    return db.query(Entry).order_by(Entry.id.desc()).all()


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = db.get(Entry, entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()
