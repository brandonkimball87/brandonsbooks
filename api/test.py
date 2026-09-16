from api.sqlconn import Database
from api.routers.basic_book_data import find_book_id, create_book_id
from api.routers.search import fetch_google_books


TEST_USER_ID = 1


# create_tables()
# list_tables()


# with Database() as db:
#     abc = find_book_id(
#             db=db,
#             user_id=TEST_USER_ID,
#             title='The Lightning Thief',
#             author_name='Rick Riordan',
#         )
#     print(abc)

#     abc = find_book_id(
#             db=db,
#             user_id=TEST_USER_ID,
#             title='The Sea of Monsters',
#             author_name='Rick Riordan',
#         )
#     print(abc)  

#     abc = create_book_id(
#             db=db,
#             user_id=TEST_USER_ID,
#             title='The Lightning Thief',
#             author_name='Rick Riordan',
#         )
#     print(abc)  

#     abc = find_book_id(
#             db=db,
#             user_id=TEST_USER_ID,
#             title='The Lightning Thief',
#             author_name='Rick Riordan',
#         )
#     print(abc)



# Test searching by title
title_results = fetch_google_books(q="The Lightning Thief")
print(f"Found {len(title_results)} books for title search:")
if title_results:
    for i, book in enumerate(title_results):
        print(book)
        print()

# # Test searching by ISBN
# isbn_results = fetch_google_books(q="9780786838653")
# print(f"\nFound {len(isbn_results)} books for ISBN search:")
# if isbn_results:
#     print(isbn_results[0])