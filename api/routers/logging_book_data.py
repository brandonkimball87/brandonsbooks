import re
from api.old_sqlconn import db
from api.routers.basic_book_data import get_or_create_book_id


def add_read_data(
    book_id: int,
    personal_rating: float | None = None,
    date_read: str | None = None,
):

    if personal_rating is not None and personal_rating not in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
        raise ValueError("Your rating must be between 0 and 5 in 0.5 increments.")

    if date_read is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_read):
        raise ValueError("Date read must be in the format YYYY-MM-DD.")

    try:
        db.Query(
            """
            insert into read_data (book_id, personal_rating, date_read)
            values (?, ?, ?)
            on conflict(book_id) do update set
                personal_rating = coalesce(excluded.personal_rating, read_data.personal_rating),
                date_read = coalesce(excluded.date_read, read_data.date_read)
            """,
            (book_id, personal_rating, date_read),
            fetch="none",
        )
    except Exception as e:
        raise ValueError(f"Could not add your read data for this book to database: {e}") from e


def mark_book_as_read(
    title: str,
    author_name: str,
    personal_rating: float | None = None,
    date_read: str | None = None,
):

    # Ensure book exists and get its id
    book_id, book_status, author_status = get_or_create_book_id(title=title, author_name=author_name)

    try:
        db.Query(
            """
            insert or ignore into lists (list_name, book_id)
            values (?, ?)
            """,
            ("read", book_id),
            fetch="none",
        )
    except Exception as e:
        raise ValueError(f"Could not add your read data for book '{title}' to database: {e}") from e

    add_read_data(book_id, personal_rating, date_read)


# def update_book_details(
#     title: str,
#     author_name: str,
#     avg_rating: float | None = None,
#     year: int | None = None,
#     num_pages: int | None = None,
#   ):
#
#     if avg_rating is not None:
#         avg_rating = round(avg_rating, 2)
#
#     if year is not None and (year < 0 or year > 9999):
#         raise ValueError("Year must be between 0 and 9999.")
#
#     if num_pages is not None and num_pages < 0:
#         raise ValueError("Number of pages cannot be negative.")
#
#     # Ensure book exists and get its id
#     book_id, book_status, author_status = get_or_create_book_id(title=title, author_name=author_name)
#
#     try:
#         db.Query(
#             """
#             update books
#             set avg_rating = coalesce(?, avg_rating),
#                 year = coalesce(?, year),
#                 num_pages = coalesce(?, num_pages)
#             where id = ?
#             """,
#             (avg_rating, year, num_pages, book_id),
#             fetch="none",
#         )
#     except Exception as e:
#         raise ValueError(f"Could not update data for '{title}' in the database: {e}") from e