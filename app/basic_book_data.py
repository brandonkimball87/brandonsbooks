from fastapi import APIRouter
from pydantic import BaseModel
from sqlconn import db


def find_author_id(author_name: str) -> dict[int, str, str]:
    author_name = author_name.strip()
    if not author_name:
        raise ValueError("Author name cannot be empty.")

    try:
        row = db.Query(
            """
            select author_id
            from authors
            where author_name = ?
            """,
            (author_name,),
            fetch="one",
            return_type="dict",
        )
        author_id = row["author_id"] if row else None
    except Exception as e:
        raise ValueError(f"Could not access author_id database: {e}") from e

    return {
        "author_id": author_id,
        "author_status": "already_present" if author_id is not None else "not_found",
    }


def create_author_id(author_name: str) -> dict[int, str]:
    author_name = author_name.strip()
    if not author_name:
        raise ValueError("Author name cannot be empty.")

    author = find_author_id(author_name=author_name)
    if author["author_id"] is not None:
        return author

    try:
        db.Query(
            """
            insert into authors (author_name)
            values (?)
            """,
            (author_name,),
            fetch="none",
        )
    except Exception as e:
        raise ValueError(
            f"Could not add author '{author_name}' to database: {e}"
        ) from e

    author = find_author_id(author_name=author_name)
    if author["author_id"] is None:
        raise ValueError(
            f"Author '{author_name}' was inserted but author_id could not be retrieved."
        )

    return {
        "author_id": author["author_id"],
        "author_status": "added",
    }


def find_book_id(title: str, author_name: str) -> dict[int, str, str]:
    title = title.strip()
    author_name = author_name.strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    if not author_name:
        raise ValueError("Author name cannot be empty.")

    author = find_author_id(author_name = author_name)

    try:
        row = db.Query(
            """
            select book_id
            from books
            where title = ? and author_id = ?
            """,
            (title, author["author_id"]),
            fetch="one",
            return_type="dict",
        )
        book_id = row["book_id"] if row else None
    except Exception as e:
        raise ValueError(f"Could not access book_id database: {e}") from e

    return {
        "book_id": book_id,
        "book_status": "already_present" if book_id is not None else "not_found",
        "author_status": author["author_status"],
    }


def create_book_id(title: str, author_name: str) -> dict[int, str, str]:
    title = title.strip()
    author_name = author_name.strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    if not author_name:
        raise ValueError("Author name cannot be empty.")

    author = create_author_id(author_name=author_name)
    book = find_book_id(title=title, author_name = author_name)
    if book["book_id"] is not None:
        return book

    try:
        db.Query(
            """
            insert into books (title, author_id)
            values (?, ?)
            """,
            (title, author["author_id"]),
            fetch="none",
        )
    except Exception as e:
        raise ValueError(f"Could not add book '{title}' to database: {e}") from e

    book = find_book_id(title=title, author_name=author_name)
    if book["book_id"] is None:
        raise ValueError(f"Book '{title}' was inserted but book_id could not be retrieved.")

    return {
        "book_id": book["book_id"],
        "book_status": "added",
        "author_status": author["author_status"],
    }


# Making the FastAPI router
router = APIRouter()

# Making the BaseModel for FastAPI requests
class AuthorRequest(BaseModel):
    author_name: str

class BookRequest(BaseModel):
    title: str
    author_name: str

# Making the FastAPI request models
@router.post("/author/")
def post_author_id(author: AuthorRequest):
    return create_author_id(author_name = author.author_name)

@router.post("/book/")
def post_book_id(book: BookRequest):
    return create_book_id(title = book.title, author_name = book.author_name)

@router.get("/author/{author_name}")
def get_author_id(author_name: str):
    return find_author_id(author_name = author_name)

@router.get("/book/")
def get_book_id(title: str, author_name: str):
    return find_book_id(title = title, author_name = author_name)