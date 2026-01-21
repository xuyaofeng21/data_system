from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# UPDATE THIS WITH YOUR MYSQL CREDENTIALS
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost/data_system"
# For development/demonstration without credentials, using SQLite:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./data_system.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
