from sqlalchemy import select
from app.models.users import Users

class UserRepository:
    def __init__(self, session):
        self.session = session
    def create(self, user: Users):
        self.session.add(user)
        self.session.flush()
        return user
    def email_exists(self, email: str):
        stmt = select(Users).where(Users.email == email)
        user = self.session.scalar(stmt)
        return user is not None
    def get_by_email(self, email: str):
        stmt = select(Users).where(Users.email == email)
        return self.session.scalar(stmt)
    def get_by_id(self, user_id: int):
        stmt = select(Users).where(Users.user_id == user_id)
        return self.session.scalar(stmt)
    def update_password(self, user: Users, password_hash: str):
        user.password = password_hash
        self.session.flush()