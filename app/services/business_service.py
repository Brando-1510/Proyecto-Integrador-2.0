from app.models.business import Business
from app.models.user_business import UserBusiness,Role

class BusinessService:
    def __init__(self,repository):
        self.repository=repository
    def create_business(
        self,user_id,business_name,type_of_business,start_of_operations,description
        ):
        try:
            business=Business(
                business_name=business_name,
                type_of_business=type_of_business,
                start_of_operations=start_of_operations,
                description=description,
                owner_id=user_id
            )
            business_created=self.repository.create_business(business)
            userBusiness=UserBusiness(
                user_id=user_id,
                business_id=business_created.business_id,
                role=Role.MANAGER
            )
            userBusiness_created=self.repository.create_user_business(userBusiness)
            self.repository.session.commit()
            return {
                "success": True,
                "business": business_created,
                "userBusiness": userBusiness_created
            }
        except Exception as e:
            self.repository.session.rollback()
            return{
                "success":False,
                "message":str(e)
            }
