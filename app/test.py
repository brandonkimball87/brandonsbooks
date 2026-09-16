from basic_book_data import get_book_id, create_book_id
from sqlconn import db
from create_tables import create_tables, list_tables

# create_tables()
# list_tables()

abc = get_book_id(
    title = 'The Lightning Thief',
    author_name = 'Rick Riordan',
)
print(abc)

abc = get_book_id(
    title = 'The Sea of Monsters',
    author_name = 'Rick Riordan',
)
print(abc)


abc = create_book_id(
    title = 'The Lightning Thief',
    author_name = 'Rick Riordan',
)
print(abc)

abc = create_book_id(
    title = 'The Sea of Monsters',
    author_name = 'Rick Riordan',
)
print(abc)