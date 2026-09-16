import os
import requests
from fastapi import APIRouter, Query

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


def fetch_google_books(q: str) -> list[dict]:
    clean_q = q.strip().replace("-", "")
    search_param = (
        f"isbn:{clean_q}"
        if (clean_q.isdigit() and len(clean_q) in (10, 13))
        else f'intitle:"{q}"'
    )

    # 1. Build request parameters
    params = {
        "q": search_param,
        "maxResults": 10,
        "printType": "books",
        "orderBy": "relevance",
    }

    # 2. Attach API key if present in environment
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(GOOGLE_BOOKS_URL, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Google Books API request failed or rate limited.")
        return []
    except Exception as e:
        print(f"Error fetching books: {e}")
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


# 2. FastAPI Router Setup
router = APIRouter(prefix="/api/py/search", tags=["Search"])


@router.get("")
def search_books(q: str = Query(..., min_length=2)):
    return fetch_google_books(q=q)