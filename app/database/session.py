from sqlalchemy.orm import sessionmaker
from app.database.connection import engine

SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

def get_session():
    return SessionLocal()