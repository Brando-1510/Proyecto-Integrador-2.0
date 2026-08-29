from sqlalchemy import select
from app.models.users import Users
from app.core.security.password import HashPassword as hp

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
    def get_by_email(self,email:str):
        stmt=select(Users).where(Users.email==email)
        user=self.session.scalar(stmt)
        return user
    def get_by_id(self, user_id: int):
        stmt = select(Users).where(Users.id == user_id)
        return self.session.scalar(stmt)
    def update_password(self, user: Users, password: str):
        user.password = password
        self.session.commit()