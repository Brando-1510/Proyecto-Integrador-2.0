from sqlalchemy import select
from app.models.user_business import UserBusiness
from app.models.business import Business


class UserBusinessRepository:
    def __init__(self, session):
        self.session = session
    def get_businesses_by_user(self, user_id: int):
        stmt = (select(UserBusiness).where(UserBusiness.user_id == user_id))
        result = self.session.scalars(stmt)
        return result.all()