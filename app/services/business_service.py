from app.models.business import Business
from app.models.user_business import UserBusiness, Role
from app.models.category import Category
DEFAULT_CATEGORIES = [
    "General",
    "Productos",
    "Servicios",
    "Promociones",
    "Combos",
    "Otros"
]
class BusinessService:
    def __init__(self, business_repository, category_repository):
        self.business_repository = business_repository
        self.category_repository = category_repository
    def create_business(self,user_id,business_name,type_of_business,start_of_operations,description):
        try:
            #*Crear el negocio
            business = Business(
                business_name=business_name,
                type_of_business=type_of_business,
                start_of_operations=start_of_operations,
                description=description,
                creator_id=user_id
            )
            business_created = self.business_repository.create_business(business)
            #*Crear relación usuario-negocio
            user_business = UserBusiness(
                user_id=user_id,
                business_id=business_created.business_id,
                role=Role.MANAGER
            )
            user_business_created = (self.business_repository.create_user_business(user_business))
            #*Crear categorías por defecto
            categories = [
                Category(
                    business_id=business_created.business_id,
                    name=name,
                    is_system=True
                )
                for name in DEFAULT_CATEGORIES
            ]
            categories_created = self.category_repository.create_many(categories)
            #*Confirmar toda la operación
            self.business_repository.session.commit()
            return {
                "success": True,
                "business": business_created,
                "userBusiness": user_business_created,
                "categories": categories_created
            }
        except Exception as e:
            self.business_repository.session.rollback()
            return {
                "success": False,
                "message": str(e)
            }