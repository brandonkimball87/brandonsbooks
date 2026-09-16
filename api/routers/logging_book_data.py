import re
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.sqlconn import Database, get_db
from api.routers.basic_book_data import create_book_id


class ReadDataRequest(BaseModel):
    user_id: int
    book_id: int
    personal_rating: float | None = None
    date_read: str | None = None


class MarkReadRequest(BaseModel):
    user_id: int
    title: str
    author_name: str
    personal_rating: float | None = None
    date_read: str | None = None


class UpdateBookDetailsRequest(BaseModel):
    user_id: int
    title: str
    author_name: str
    avg_rating: float | None = None
    year: int | None = Field(default=None, ge=0, le=9999)
    num_pages: int | None = Field(default=None, ge=0)


def add_read_data(
    db: Database,
    user_id: int,
    book_id: int,
    personal_rating: float | None = None,
    date_read: str | None = None,
) -> dict[str, Any]:

    valid_ratings = {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0}
    if personal_rating is not None and personal_rating not in valid_ratings:
        raise HTTPException(
            status_code=400,
            detail="Your rating must be between 0 and 5 in 0.5 increments.",
        )

    if date_read is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_read):
        raise HTTPException(
            status_code=400,
            detail="Date read must be in the format YYYY-MM-DD.",
        )

    db.execute_query(
        """
        insert into read_data (user_id, book_id, personal_rating, date_read)
        values (:user_id, :book_id, :personal_rating, :date_read)
        on conflict (user_id, book_id) do update set
            personal_rating = coalesce(excluded.personal_rating, read_data.personal_rating),
            date_read = coalesce(excluded.date_read, read_data.date_read)
        """,
        {
            "user_id": user_id,
            "book_id": book_id,
            "personal_rating": personal_rating,
            "date_read": date_read,
        },
        fetch="none",
    )

    return {"message": "Read data successfully saved."}


def mark_book_as_read(
    db: Database,
    user_id: int,
    title: str,
    author_name: str,
    personal_rating: float | None = None,
    date_read: str | None = None,
) -> dict[str, Any]:

    # Ensure book exists and get its details
    book_res = create_book_id(db, user_id=user_id, title=title, author_name=author_name)
    book_id = book_res["book_id"]

    # PostgreSQL equivalent of "INSERT OR IGNORE" using ON CONFLICT DO NOTHING
    db.execute_query(
        """
        insert into lists (user_id, list_name, book_id)
        values (:user_id, :list_name, :book_id)
        on conflict (user_id, list_name, book_id) do nothing
        """,
        {"user_id": user_id, "list_name": "read", "book_id": book_id},
        fetch="none",
    )

    add_read_data(
        db=db,
        user_id=user_id,
        book_id=book_id,
        personal_rating=personal_rating,
        date_read=date_read,
    )

    return {
        "message": f"Book '{title}' marked as read.",
        "book_id": book_id,
        "author_status": book_res["author_status"],
        "book_status": book_res["book_status"],
    }


def update_book_details(
    db: Database,
    user_id: int,
    title: str,
    author_name: str,
    avg_rating: float | None = None,
    year: int | None = None,
    num_pages: int | None = None,
) -> dict[str, Any]:

    if avg_rating is not None:
        avg_rating = round(avg_rating, 2)

    if year is not None and (year < 0 or year > 9999):
        raise HTTPException(status_code=400, detail="Year must be between 0 and 9999.")

    if num_pages is not None and num_pages < 0:
        raise HTTPException(status_code=400, detail="Number of pages cannot be negative.")

    book_res = create_book_id(db, user_id=user_id, title=title, author_name=author_name)
    book_id = book_res["book_id"]

    db.execute_query(
        """
        update books
        set avg_rating = coalesce(:avg_rating, avg_rating),
            year = coalesce(:year, year),
            num_pages = coalesce(:num_pages, num_pages)
        where user_id = :user_id and book_id = :book_id
        """,
        {
            "avg_rating": avg_rating,
            "year": year,
            "num_pages": num_pages,
            "user_id": user_id,
            "book_id": book_id,
        },
        fetch="none",
    )

    return {"message": f"Details for '{title}' updated successfully."}


router = APIRouter()


@router.post("/read-data/")
def post_read_data(req: ReadDataRequest, db: Database = Depends(get_db)):
    return add_read_data(
        db,
        user_id=req.user_id,
        book_id=req.book_id,
        personal_rating=req.personal_rating,
        date_read=req.date_read,
    )


@router.post("/mark-read/")
def post_mark_read(req: MarkReadRequest, db: Database = Depends(get_db)):
    return mark_book_as_read(
        db,
        user_id=req.user_id,
        title=req.title,
        author_name=req.author_name,
        personal_rating=req.personal_rating,
        date_read=req.date_read,
    )


@router.put("/update-details/")
def put_update_details(req: UpdateBookDetailsRequest, db: Database = Depends(get_db)):
    return update_book_details(
        db,
        user_id=req.user_id,
        title=req.title,
        author_name=req.author_name,
        avg_rating=req.avg_rating,
        year=req.year,
        num_pages=req.num_pages,
    )