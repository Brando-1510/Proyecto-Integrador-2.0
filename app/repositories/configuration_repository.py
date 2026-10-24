
from sqlalchemy import select, update, delete, exists
from sqlalchemy.orm import selectinload
from app.models.movement import Movement
from app.models.sale import Sale
from app.models.imports import Import
from app.models.user_business import UserBusiness, Role
from app.models.users import Users
from app.models.business import Business, TypeOfBusiness
from app.models.category import Category


class ConfigurationRepository:
    def __init__(self, session):
        self.session = session

    # ---------------------------------------------------------
    # INFORMACIÓN DEL NEGOCIO
    # ---------------------------------------------------------
    def get_business(self, business_id: int) -> Business | None:
        stmt = (
            select(Business)
            .options(selectinload(Business.categories))
            .where(Business.business_id == business_id)
            .execution_options(populate_existing=True)
        )

        return self.session.scalar(stmt)

    def modify_business(
        self,
        business_id: int,
        business_name: str | None = None,
        type_of_business: TypeOfBusiness | None = None,
        description: str | None = None,
    ) -> Business | None:
        business = self.session.get(Business, business_id)

        if business is None:
            return None

        if business_name is not None:
            business.business_name = business_name

        if type_of_business is not None:
            business.type_of_business = type_of_business

        if description is not None:
            business.description = description

        return business

    def reassign_sales_category(
        self,
        business_id: int,
        category_id: int,
        new_category_id: int,
    ) -> int:
        stmt = (
            update(Sale)
            .where(
                Sale.business_id == business_id,
                Sale.category_id == category_id,
            )
            .values(category_id=new_category_id)
        )

        result = self.session.execute(stmt)
        return result.rowcount or 0

    # ---------------------------------------------------------
    # CATEGORÍAS
    # ---------------------------------------------------------

    def delete_category(
        self,
        business_id: int,
        category_id: int,
    ) -> bool:
        category = self.session.scalar(
            select(Category).where(
                Category.category_id == category_id,
                Category.business_id == business_id,
            )
        )

        if category is None or category.is_system:
            return False

        other_category_id = self.session.scalar(
            select(Category.category_id).where(
                Category.business_id == business_id,
                Category.name == "Otros",
                Category.is_system.is_(True),
            )
        )

        if other_category_id is None:
            raise ValueError(
                "No existe la categoría predeterminada 'Otros'."
            )

        self.reassign_sales_category(
            business_id=business_id,
            category_id=category_id,
            new_category_id=other_category_id,
        )

        self.session.delete(category)
        self.session.flush()

        return True

    def add_categories(
        self,
        business_id: int,
        categories: list[str],
    ) -> list[Category]:
        nuevas_categorias = []

        for nombre in categories:
            categoria = Category(
                business_id=business_id,
                name=nombre,
                is_system=False,
            )

            self.session.add(categoria)
            nuevas_categorias.append(categoria)

        self.session.flush()
        return nuevas_categorias

    # ---------------------------------------------------------
    # USUARIOS Y EMPLEADOS
    # ---------------------------------------------------------

    def get_users(
        self,
        name: str | None = None,
        email: str | None = None,
    ):
        stmt = select(
            Users.username,
            Users.email,
        ).where(Users.is_admin != 1)

        if name is not None:
            stmt = stmt.where(
                Users.username.like(f"%{name}%")
            )

        if email is not None:
            stmt = stmt.where(
                Users.email.like(f"%{email}%")
            )

        return self.session.execute(stmt).all()

    def get_employees(
        self,
        business_id: int,
        name: str | None = None,
        email: str | None = None,
    ):
        stmt = (
            select(
                Users.username,
                Users.email,
                UserBusiness.role,
                UserBusiness.created_at,
            )
            .where(
                UserBusiness.business_id == business_id,
                UserBusiness.role != Role.ADMIN,
            )
            .join(
                Users,
                UserBusiness.user_id == Users.user_id,
            )
        )

        if name is not None:
            stmt = stmt.where(
                Users.username.like(f"%{name}%")
            )

        if email is not None:
            stmt = stmt.where(
                Users.email.like(f"%{email}%")
            )

        return self.session.execute(stmt).all()

    def get_user_id(self, correo: str):
        stmt = select(Users.user_id).where(
            Users.email == correo
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_userBusiness_relationship(
        self,
        user_id: int,
        business_id: int,
    ):
        stmt = select(
            exists().where(
                UserBusiness.user_id == user_id,
                UserBusiness.business_id == business_id,
            )
        )

        return self.session.scalar(stmt)

    def is_admin(self, user_id: int) -> bool:
        stmt = select(Users.is_admin).where(
            Users.user_id == user_id
        )

        return bool(self.session.scalar(stmt))

    def is_creator(
        self,
        user_id: int,
        business_id: int,
    ) -> bool:
        stmt = select(
            exists().where(
                Business.business_id == business_id,
                Business.creator_id == user_id,
            )
        )

        return bool(self.session.scalar(stmt))

    def link_user_to_business(
        self,
        user_id: int,
        business_id: int,
        role: Role,
    ) -> None:
        relationship = UserBusiness(
            user_id=user_id,
            business_id=business_id,
            role=role,
        )

        self.session.add(relationship)
        self.session.flush()

    def unlink_user_from_business(
        self,
        user_id: int,
        business_id: int,
    ) -> bool:
        stmt = delete(UserBusiness).where(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id,
        )

        result = self.session.execute(stmt)
        return (result.rowcount or 0) > 0

    # ---------------------------------------------------------
    # OPERACIONES CRÍTICAS
    # ---------------------------------------------------------

    def delete_import(
        self,
        business_id: int,
        import_id: int,
    ) -> bool:
        # Verificar que la importación pertenezca al negocio.
        stmt = select(Import.import_id).where(
            Import.import_id == import_id,
            Import.business_id == business_id,
        )

        if self.session.scalar(stmt) is None:
            return False

        # Eliminar las ventas de la importación.
        self.session.execute(
            delete(Sale).where(
                Sale.business_id == business_id,
                Sale.import_id == import_id,
            )
        )

        # Eliminar los movimientos de la importación.
        self.session.execute(
            delete(Movement).where(
                Movement.business_id == business_id,
                Movement.import_id == import_id,
            )
        )

        # Eliminar la importación.
        self.session.execute(
            delete(Import).where(
                Import.import_id == import_id,
                Import.business_id == business_id,
            )
        )

        # El servicio confirma o revierte la transacción.
        return True

    def delete_business(self, business_id: int) -> bool:
        # Verificar que el negocio exista.
        stmt = select(Business.business_id).where(
            Business.business_id == business_id
        )

        if self.session.scalar(stmt) is None:
            return False

        # Eliminar las ventas.
        self.session.execute(
            delete(Sale).where(
                Sale.business_id == business_id
            )
        )

        # Eliminar los movimientos.
        self.session.execute(
            delete(Movement).where(
                Movement.business_id == business_id
            )
        )

        # Eliminar las importaciones.
        self.session.execute(
            delete(Import).where(
                Import.business_id == business_id
            )
        )

        # Eliminar las categorías.
        self.session.execute(
            delete(Category).where(
                Category.business_id == business_id
            )
        )

        # Eliminar las vinculaciones de usuarios.
        self.session.execute(
            delete(UserBusiness).where(
                UserBusiness.business_id == business_id
            )
        )

        # Eliminar el negocio.
        self.session.execute(
            delete(Business).where(
                Business.business_id == business_id
            )
        )

        # El servicio confirma o revierte la transacción.
        return True
