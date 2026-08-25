#Modulo usado para crear el engine
from sqlalchemy import create_engine
from app.config.settings import DATABASE_URL
#*El engine representa la conexión que SQLAlchemy utilizará para comunicarse con la BD.
engine = create_engine(DATABASE_URL,echo=False)