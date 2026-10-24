from app.database.connection import SessionLocal
from app.repositories.user_business_repository import UserBusinessRepository

class UserBusinessService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def get_user_businesses(self, user_id: int):
        with self.session_factory() as session:
            repository = UserBusinessRepository(session)
            result = repository.get_businesses_by_user(user_id)
            # Cargar los atributos escalares antes de cerrar la sesión.
            for user_business in result:
                session.expunge(user_business)
            return result
