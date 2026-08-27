from app.database.base import Base
from app.database.connection import engine

# Importar modelos para que SQLAlchemy los conozca
from app.models.users import Users
from app.models.business import Business
from app.models.user_business import UserBusiness
from app.models.recovery import Recovery

def init_db():
    Base.metadata.create_all(bind=engine)