from fastapi import FastAPI
from basic_book_data import router
import uvicorn

app = FastAPI()
app.include_router(router, prefix = "/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# run "uvicorn main:app --reload" in command line if i remove the "if __name__ == __main__:" part

# Host options for the uvicorn server:
#1. host="0.0.0.0"- anyone
    # computer access: http://localhost:8000/docs or http://127.0.0.1:8000/docs or http://192.168.0.174:8000/docs (IP address)  
    # phone access: http://192.168.0.174:8000/docs (IP address) 
    # uvicorn.run(app, host = "0.0.0.0", port = 8000)
#2. host="127.0.0.1"- only computer
    # only computer: http://localhost:8000/docs or http://127.0.0.1:8000/docs
    # uvicorn.run(app, host = "127.0.0.1", port = 8000)
#3. host="192.168.0.174"- anyone on my wifi
    # computer or phone access: http://192.168.0.174:8000/docs (IP address)  
    # uvicorn.run(app, host = "192.168.0.174", port = 8000)