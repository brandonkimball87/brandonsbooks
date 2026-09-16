from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from api.sqlconn import Database, get_db


class AuthorRequest(BaseModel):
    user_id: int
    author_name: str


class BookRequest(BaseModel):
    user_id: int
    title: str
    author_name: str


def find_author_id(db: Database, user_id: int, author_name: str) -> dict[str, Any]:
    author_name = author_name.strip()
    if not author_name:
        raise HTTPException(status_code=400, detail="Author name cannot be empty.")

    row = db.execute_query(
        """
        select author_id
        from authors
        where user_id = :user_id and author_name = :author_name
        """,
        {"user_id": user_id, "author_name": author_name},
        fetch="one",
        return_type="dict",
    )
    author_id = row["author_id"] if row else None

    return {
        "author_id": author_id,
        "author_status": "already_present" if author_id is not None else "not_found",
    }


def create_author_id(db: Database, user_id: int, author_name: str) -> dict[str, Any]:
    author_name = author_name.strip()
    if not author_name:
        raise HTTPException(status_code=400, detail="Author name cannot be empty.")

    author = find_author_id(db, user_id=user_id, author_name=author_name)
    if author["author_id"] is not None:
        return author

    # Use RETURNING author_id to fetch the generated SERIAL ID in one query
    row = db.execute_query(
        """
        insert into authors (user_id, author_name)
        values (:user_id, :author_name)
        returning author_id
        """,
        {"user_id": user_id, "author_name": author_name},
        fetch="one",
        return_type="dict",
    )

    return {
        "author_id": row["author_id"],
        "author_status": "added",
    }


def find_book_id(db: Database, user_id: int, title: str, author_name: str) -> dict[str, Any]:
    title = title.strip()
    author_name = author_name.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if not author_name:
        raise HTTPException(status_code=400, detail="Author name cannot be empty.")

    author = find_author_id(db, user_id=user_id, author_name=author_name)
    if author["author_id"] is None:
        return {
            "book_id": None,
            "book_status": "not_found",
            "author_status": "not_found",
        }

    row = db.execute_query(
        """
        select book_id
        from books
        where user_id = :user_id and title = :title and author_id = :author_id
        """,
        {"user_id": user_id, "title": title, "author_id": author["author_id"]},
        fetch="one",
        return_type="dict",
    )
    book_id = row["book_id"] if row else None

    return {
        "book_id": book_id,
        "book_status": "already_present" if book_id is not None else "not_found",
        "author_status": author["author_status"],
    }


def create_book_id(db: Database, user_id: int, title: str, author_name: str) -> dict[str, Any]:
    title = title.strip()
    author_name = author_name.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if not author_name:
        raise HTTPException(status_code=400, detail="Author name cannot be empty.")

    author = create_author_id(db, user_id=user_id, author_name=author_name)
    book = find_book_id(db, user_id=user_id, title=title, author_name=author_name)
    if book["book_id"] is not None:
        return book

    row = db.execute_query(
        """
        insert into books (user_id, title, author_id)
        values (:user_id, :title, :author_id)
        returning book_id
        """,
        {"user_id": user_id, "title": title, "author_id": author["author_id"]},
        fetch="one",
        return_type="dict",
    )

    return {
        "book_id": row["book_id"],
        "book_status": "added",
        "author_status": author["author_status"],
    }


router = APIRouter()


@router.post("/author/")
def post_author_id(author: AuthorRequest, db: Database = Depends(get_db)):
    return create_author_id(db, user_id=author.user_id, author_name=author.author_name)


@router.post("/book/")
def post_book_id(book: BookRequest, db: Database = Depends(get_db)):
    return create_book_id(db, user_id=book.user_id, title=book.title, author_name=book.author_name)


@router.get("/author/{author_name}")
def get_author_id(author_name: str, user_id: int = Query(...), db: Database = Depends(get_db)):
    return find_author_id(db, user_id=user_id, author_name=author_name)


@router.get("/book/")
def get_book_id(title: str, author_name: str, user_id: int = Query(...), db: Database = Depends(get_db)):
    return find_book_id(db, user_id=user_id, title=title, author_name=author_name)