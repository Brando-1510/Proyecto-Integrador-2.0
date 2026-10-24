from app.database.connection import SessionLocal
from app.repositories.business_repository import BusinessRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.models.business import Business
from app.models.user_business import Role
from app.models.category import Category

DEFAULT_CATEGORIES = [
    "General", "Productos", "Servicios",
    "Promociones", "Combos", "Otros"
]

class BusinessService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def create_business(
        self,user_id,business_name,type_of_business,start_of_operations,description
    ):
        try:
            with self.session_factory.begin() as session:
                business_repository = BusinessRepository(session)
                category_repository = CategoryRepository(session)
                user_repository = UserRepository(session)
                user_business_repository = UserBusinessRepository(session)
                # Crear el negocio.
                business = Business(
                    business_name=business_name,
                    type_of_business=type_of_business,
                    start_of_operations=start_of_operations,
                    description=description,
                    creator_id=user_id
                )
                business_created = (business_repository.create_business(business))
                # Vincular al creador como gerente.
                manager_created = (
                    user_business_repository.create_relationship(
                        user_id=user_id,
                        business_id=business_created.business_id,
                        role=Role.MANAGER
                    )
                )
                #*Vincular a los administradores del sistema.
                admins = user_repository.get_admin_users()
                if not admins:
                    raise ValueError("No existe ningún administrador del sistema.")
                admin_relationships = [
                    user_business_repository.create_relationship(
                        user_id=admin.user_id,
                        business_id=business_created.business_id,
                        role=Role.ADMIN
                    )
                    for admin in admins
                ]
                # Crear las categorías predeterminadas.
                categories = [
                    Category(
                        business_id=business_created.business_id,
                        name=name,
                        is_system=True
                    )
                    for name in DEFAULT_CATEGORIES
                ]
                categories_created = (category_repository.create_many(categories))
                session.flush()
                result = {
                    "success": True,
                    "business": business_created,
                    "manager": manager_created,
                    "admins": admin_relationships,
                    "categories": categories_created
                }
                objects_to_detach = [
                    business_created,
                    manager_created,
                    *admin_relationships,
                    *categories_created
                ]
                for obj in objects_to_detach:
                    session.expunge(obj)
            # La transacción se confirma al salir del bloque.
            return result
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }