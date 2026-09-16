import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing!")

# Engine configured with pool_pre_ping for serverless Neon connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Database:
    def __init__(self):
        self.session = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.session.close()

    def execute_query(self, sql: str, params: dict = None, fetch: str = "all", return_type: str = "dict"):
        if params is None:
            params = {}

        try:
            statement = text(sql)
            result = self.session.execute(statement, params)

            if fetch == "none":
                self.session.commit()
                return {"rowcount": result.rowcount}

            if fetch == "one":
                row = result.fetchone()
                self.session.commit()  # Close the read transaction
                row_dict = dict(row._mapping) if row else None
                
                if return_type == "dict":
                    return row_dict
                return pd.DataFrame([row_dict]) if row_dict is not None else pd.DataFrame()

            # Default: fetch == "all"
            rows = result.fetchall()
            self.session.commit()  # Close the read transaction
            data = [dict(r._mapping) for r in rows]
            
            if return_type == "dict":
                return data
            return pd.DataFrame(data)

        except Exception as e:
            self.session.rollback()
            raise e

    def close(self):
        self.session.close()

# FastAPI Dependency
def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()