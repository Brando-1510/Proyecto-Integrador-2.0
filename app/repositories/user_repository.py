from sqlalchemy import select
from app.models.users import Users
from datetime import date
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
    def get_admin_users(self):
        stmt = select(Users).where(Users.is_admin == True)
        return self.session.scalars(stmt).all()
    #*Metodos para el modulo de perfil
    def modify_user(
        self,user_id:int,username:str | None=None,email:str | None=None,fecha:date | None=None
    ) -> Users | None:
        user=self.session.get(Users,user_id)
        if username is not None:
            user.username=username
        if email is not None:
            user.email=email
        if fecha is not None:
            user.birth_date=fecha
        return user
