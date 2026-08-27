from sqlalchemy import select
from app.models.users import Users

class UserRepository:
    def __init__(self, session):
        self.session = session
    def create(self, user: Users):
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    def email_exist(self, email: str):
        stmt = select(Users).where(Users.email == email)
        user = self.session.scalar(stmt)
        return user is not None