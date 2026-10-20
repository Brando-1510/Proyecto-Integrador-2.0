from datetime import date
from decimal import Decimal
from sqlalchemy import select, func, case, desc,update,delete
from app.models.movement import Movement
from app.models.sale import Sale
from app.models.imports import Import
from app.models.users import Users
from app.models.business import Business,TypeOfBusiness
from app.models.category import Category

class ConfigurationRepository:
    def __init__(self,session):
        self.session=session

#TODOS los metodos relacionados a la tab de Información del negocio
    #*Modificar un negocio en base a lo que mande la interfaz
    def modify_business(
    self,business_id: int,business_name: str | None = None,
    type_of_business: TypeOfBusiness | None = None,description: str | None = None,
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
        self,business_id: int,category_id: int,new_category_id: int,
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
        return result.rowcount
    #!Eliminar categorias
    def delete_category(self,business_id: int,category_id: int,) -> bool:
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
            raise ValueError("No existe la categoría predeterminada 'Otros'.")
        self.reassign_sales_category(
            business_id=business_id,
            category_id=category_id,
            new_category_id=other_category_id,
        )
        self.session.delete(category)
        self.session.flush()
        return True
    #*Añadir categorias
    def add_categories(self,business_id: int,categories: list[str]) -> list[Category]:
        nuevas_categorias = []
        for nombre in categories:
            categoria = Category(
                business_id=business_id,
                name=nombre,
                is_system=False
            )
            self.session.add(categoria)
            nuevas_categorias.append(categoria)
        self.session.flush()
        return nuevas_categorias