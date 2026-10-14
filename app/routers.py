from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Entry
from app.schemas import EntryCreate, EntryRead

router = APIRouter(prefix="/entries", tags=["Entries"])


@router.post(
    "",
    response_model=EntryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    entry: EntryCreate,
    db: AsyncSession = Depends(get_db),
):
    db_entry = Entry(content=entry.content)
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


@router.get("", response_model=list[EntryRead])
async def get_entries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entry).order_by(Entry.id.desc()))
    return result.scalars().all()


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
):
    entry = await db.get(Entry, entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    await db.delete(entry)
    await db.commit()
