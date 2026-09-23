from datetime import date as dt_date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,String,Text,Numeric,Enum as SQLEnum,func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.imports import Import
    from app.models.users import Users

class MovementType(Enum):
    INCOME = "Ingreso"
    EXPENSE = "Gasto"
class IncomeCategory(Enum):
    SALES = "Ventas"
    SERVICES = "Servicios"
    OTHER_INCOME = "Otros ingresos"
class ExpenseCategory(Enum):
    PURCHASES = "Compras"
    PERSONNEL = "Personal"
    BASIC_SERVICES = "Servicios básicos"
    RENT = "Alquiler"
    TRANSPORT = "Transporte"
    MAINTENANCE = "Mantenimiento"
    ADVERTISING = "Publicidad"
    TAXES = "Impuestos"
    OTHER = "Otros"
class PaymentMethod(Enum):
    CASH = "Efectivo"
    CARD = "Tarjeta"
    TRANSFER = "Transferencia"
    OTHER = "Otro"

class Movement(Base):
    __tablename__ = "movements"
    movement_id: Mapped[intpk]
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.business_id"),nullable=False)
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.import_id"),nullable=False)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"),nullable=True)

    date: Mapped[dt_date] = mapped_column(nullable=False)
    type: Mapped[MovementType] = mapped_column(
        SQLEnum(
            MovementType,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ]
        ),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SQLEnum(
            PaymentMethod,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ]
        ),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    business: Mapped["Business"] = relationship(back_populates="movements")
    import_record: Mapped["Import"] = relationship(back_populates="movements")
    creator: Mapped["Users"] = relationship(back_populates="created_movements",foreign_keys=[created_by])
    updater: Mapped["Users | None"] = relationship(
        back_populates="updated_movements",
        foreign_keys=[updated_by]
    )
