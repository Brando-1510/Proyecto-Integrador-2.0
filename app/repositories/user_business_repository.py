from sqlalchemy import select
from app.models.user_business import UserBusiness
from app.models.business import Business
from app.models.users import Users
from sqlalchemy.orm import joinedload,selectinload
class UserBusinessRepository:
    def __init__(self, session):
        self.session = session
    def get_businesses_by_user(self, user_id: int):
        stmt = (
            select(UserBusiness)
            .options(
                joinedload(UserBusiness.business).selectinload(
                    Business.categories
                ),
                joinedload(UserBusiness.user),
            )
            .where(UserBusiness.user_id == user_id)
        )
        result = self.session.scalars(stmt)
        return result.all()
    def create_relationship(self, user_id, business_id, role):
        user_business = UserBusiness(
            user_id=user_id,
            business_id=business_id,
            role=role
        )
        self.session.add(user_business)
        self.session.flush()
        return user_business
    def exists_relationship(self, user_id: int, business_id: int) -> bool:
        stmt = select(UserBusiness.user_id).where(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id,
        ).limit(1)
        return self.session.scalar(stmt) is not None
    def get_employees(self,business_id:int,user_id:int):
        stmt=(
            select(
                Users.username.label("Username"),UserBusiness.role.label("Rol"),
                Users.email.label("Email")
            )
            .where(
                UserBusiness.business_id == business_id, Users.user_id != user_id
            )
            .join(Users, UserBusiness.user_id == Users.user_id)
        )
        resultados = self.session.execute(stmt).all()
        return resultados