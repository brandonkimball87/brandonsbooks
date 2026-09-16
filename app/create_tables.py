from sqlconn import db


CREATE_AUTHORS_TABLE = """
create table if not exists authors (
    author_id integer primary key autoincrement,
    author_name text not null unique
);
"""

CREATE_BOOKS_TABLE = """
create table if not exists books (
    book_id integer primary key autoincrement,
    title text not null,
    author_id integer not null,
    year integer,
    avg_rating float,
    num_pages integer,
    foreign key (author_id) references authors(author_id),
    unique (title, author_id)
);
"""

CREATE_READ_DATA_TABLE = """
create table if not exists read_data (
    read_data_id integer primary key autoincrement,
    personal_rating float,
    date_read text
        check (date_read GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    book_id integer not null,
    foreign key (book_id) references books(book_id),
    unique (book_id)
);
"""

CREATE_LISTS_TABLE = """
create table if not exists lists (
    list_id integer primary key autoincrement,
    list_name text not null,
    book_id integer not null,
    foreign key (book_id) references books(book_id),
    unique (list_name, book_id)
);
"""


def create_tables():
    db.Query(CREATE_AUTHORS_TABLE)
    db.Query(CREATE_BOOKS_TABLE)
    db.Query(CREATE_READ_DATA_TABLE)
    db.Query(CREATE_LISTS_TABLE)
    print("Database initialized.")


LIST_ALL_TABLES = """
select name as table_name
from sqlite_master
where type='table'
    and name not like 'sqlite_%'
order by name;
"""


def list_tables():
    table_list = db.Query(LIST_ALL_TABLES, fetch="all", return_type="dict")
    print("Tables in the database:")
    for num, table in enumerate(table_list, start=1):
        print(f"\t{num}. {table['table_name']}")


if __name__ == "__main__":
    create_tables()
    list_tables()