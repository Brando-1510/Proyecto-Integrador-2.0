from datetime import date as dt_date, datetime
from decimal import Decimal
from typing import Annotated, TYPE_CHECKING
from sqlalchemy import ForeignKey,String,Numeric,func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.imports import Import
    from app.models.category import Category
    from app.models.users import Users

class Sale(Base):
    __tablename__ = "sales"
    sale_id: Mapped[intpk]
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.business_id"),nullable=False)
    import_id: Mapped[int] = mapped_column(ForeignKey("imports.import_id"),nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"),nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"),nullable=True)
    date: Mapped[dt_date] = mapped_column(nullable=False)
    product_service: Mapped[str] = mapped_column(String(150),nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    business: Mapped["Business"] = relationship(back_populates="sales")
    import_record: Mapped["Import"] = relationship(back_populates="sales")
    category: Mapped["Category"] = relationship(back_populates="sales")
    creator: Mapped["Users"] = relationship(back_populates="created_sales",foreign_keys=[created_by])
    updater: Mapped["Users | None"] = relationship(
    back_populates="updated_sales",foreign_keys=[updated_by])