from sqlalchemy import select
from app.models.business import Business
from app.models.user_business import UserBusiness

class BusinessRepository:
    def __init__(self,session):
        self.session=session
    def create_business(self,business:Business):
        self.session.add(business)
        self.session.flush()
        return business
    def create_user_business(self,userBusiness:UserBusiness):
        self.session.add(userBusiness)
        self.session.flush()
        return userBusiness