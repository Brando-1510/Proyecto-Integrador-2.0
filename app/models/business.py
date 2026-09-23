from datetime import date, datetime
from enum import Enum
from typing import Annotated, TYPE_CHECKING
from sqlalchemy import ForeignKey,String,Text,Enum as SQLEnum,func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.users import Users
    from app.models.user_business import UserBusiness
    from app.models.imports import Import
    from app.models.movement import Movement
    from app.models.sale import Sale
    from app.models.category import Category
class TypeOfBusiness(Enum):
    BARBERSHOP = "Barbería"
    CLOTHSTORE = "Tienda de Ropa"
    COFFEESHOP = "Cafetería"
    DRUGSTORE = "Farmacia"
    RESTAURANT = "Restaurante"
    HARDWARESTORE = "Ferretería"
    GROCERYSTORE = "Pulpería"
    OTHER = "Otro"

class Business(Base):
    __tablename__ = "businesses"
    business_id: Mapped[intpk]
    business_name: Mapped[str] = mapped_column(String(150),nullable=False)
    type_of_business: Mapped[TypeOfBusiness] = mapped_column(
        SQLEnum(
            TypeOfBusiness,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ]
        ),
        default=TypeOfBusiness.OTHER,
        nullable=False
    )
    start_of_operations: Mapped[date | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text,nullable=True)
    logo: Mapped[str | None] = mapped_column(String(255),nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    #*Relaciones
    creator: Mapped["Users"] = relationship(back_populates="created_businesses")
    user_relationships: Mapped[list["UserBusiness"]] = relationship(back_populates="business")
    imports: Mapped[list["Import"]] = relationship(back_populates="business")
    movements: Mapped[list["Movement"]] = relationship(back_populates="business")
    sales: Mapped[list["Sale"]] = relationship(back_populates="business")
    categories: Mapped[list["Category"]] = relationship(back_populates="business")