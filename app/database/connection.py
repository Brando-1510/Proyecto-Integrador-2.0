from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import DATABASE_URL

#Modulo usado para crear el engine
#*El engine representa la conexión que SQLAlchemy utilizará para comunicarse con la BD.
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
def get_session():
    return SessionLocal()