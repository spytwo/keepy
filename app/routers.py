from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Entry
from app.schemas import EntryCreate, EntryRead

router = APIRouter(prefix="/entries", tags=["Entries"])


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found",
        )

    db.delete(entry)
    db.commit()
