from sqlalchemy import select
from app.models.user_business import UserBusiness
class UserBusinessRepository:
    def __init__(self, session):
        self.session = session
    def get_businesses_by_user(self, user_id: int):
        stmt = select(UserBusiness).where(
            UserBusiness.user_id == user_id)
        result = self.session.scalars(stmt)
        return result.all()
    def create_relationship(self, user_id, business_id, role):
        user_business = UserBusiness(
            user_id=user_id,
            business_id=business_id,
            role=role
        )
        self.session.add(user_business)
        return user_business