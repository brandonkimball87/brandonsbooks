# api/routers/search.py
from fastapi import APIRouter, Query
import requests

router = APIRouter(prefix="/api/py/search", tags=["Search"])

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

@router.get("")
def search_books(q: str = Query(..., min_length=2)):
    # Clean query logic (ISBN vs. Title)
    clean_q = q.strip().replace("-", "")
    search_param = f"isbn:{clean_q}" if (clean_q.isdigit() and len(clean_q) in (10, 13)) else f'intitle:"{q}"'

    response = requests.get(GOOGLE_BOOKS_URL, params={
        "q": search_param,
        "maxResults": 10,
        "printType": "books",
        "orderBy": "relevance"
    })
    
    if response.status_code != 200:
        return []

    data = response.json()
    cleaned_books = []
    
    for item in data.get("items", []):
        vol = item.get("volumeInfo", {})
        authors = vol.get("authors", ["Unknown Author"])
        pub_date = vol.get("publishedDate", "")
        
        images = vol.get("imageLinks", {})
        cover_url = images.get("thumbnail", images.get("smallThumbnail", "")).replace("http://", "https://")

        cleaned_books.append({
            "google_id": item.get("id"),
            "title": vol.get("title", "Unknown Title"),
            "authors": ", ".join(authors),
            "page_count": vol.get("pageCount", 0),
            "year": pub_date.split("-")[0] if pub_date else "N/A",
            "cover_url": cover_url
        })

    return cleaned_books