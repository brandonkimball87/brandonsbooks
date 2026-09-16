from api.sqlconn import Database

CREATE_AUTHORS_TABLE = """
create table if not exists authors (
    author_id serial primary key,
    user_id int not null,
    author_name varchar(255) not null,
    unique (user_id, author_name)
);
"""

CREATE_BOOKS_TABLE = """
create table if not exists books (
    book_id serial primary key,
    user_id int not null,
    title varchar(255) not null,
    author_id int not null,
    year int,
    avg_rating float,
    num_pages int,
    foreign key (author_id) references authors(author_id) on delete cascase,
    unique (user_id, title, author_id)
);
"""

CREATE_READ_DATA_TABLE = """
create table if not exists read_data (
    read_data_id serial primary key,
    user_id int not null,
    personal_rating float,
    date_read varchar(10) CHECK (date_read ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'),
    book_id int not null,
    foreign key (book_id) references books(book_id) on delete cascase,
    unique (user_id, book_id)
);
"""

CREATE_LISTS_TABLE = """
create table if not exists lists (
    list_id serial primary key,
    user_id int not null,
    list_name varchar(255) not null,
    book_id int not null,
    foreign key (book_id) references books(book_id) on delete cascase,
    unique (user_id, list_name, book_id)
);
"""

LIST_ALL_TABLES = """
select table_name 
from information_schema.tables 
where table_schema = 'public' 
order by table_name;
"""


def create_tables():
    db = Database()
    db.execute_query(CREATE_AUTHORS_TABLE, fetch="none")
    db.execute_query(CREATE_BOOKS_TABLE, fetch="none")
    db.execute_query(CREATE_READ_DATA_TABLE, fetch="none")
    db.execute_query(CREATE_LISTS_TABLE, fetch="none")
    print("Database initialized.")


def list_tables():
    db = Database()
    table_list = db.execute_query(LIST_ALL_TABLES, fetch="all", return_type="dict")
    print("Tables in the database:")
    for num, table in enumerate(table_list, start=1):
        print(f"\t{num}. {table['table_name']}")


if __name__ == "__main__":
    create_tables()
    list_tables()