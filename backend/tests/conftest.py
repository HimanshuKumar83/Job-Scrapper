import os

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpulse.db"

from app.db.database import create_db_and_tables

create_db_and_tables()
