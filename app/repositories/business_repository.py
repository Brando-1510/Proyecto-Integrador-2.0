from app.models.business import Business
from app.models.user_business import UserBusiness
from sqlalchemy import select

class BusinessRepository:
    def __init__(self, session):
        self.session = session
    def create_business(self, business: Business):
        self.session.add(business)
        self.session.flush()
        return business
    def create_user_business(self, user_business: UserBusiness):
        self.session.add(user_business)
        self.session.flush()
        return user_business
    def get_by_id(self, business_id: int):
        stmt = (select(Business).where(Business.business_id == business_id))
        return self.session.scalar(stmt)