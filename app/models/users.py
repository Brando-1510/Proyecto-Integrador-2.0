from datetime import date, datetime
from typing import Annotated, TYPE_CHECKING
from sqlalchemy import String, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.user_business import UserBusiness
    from app.models.recovery import Recovery
    from app.models.movement import Movement
    from app.models.sale import Sale
    from app.models.imports import Import

class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String(150),nullable=False)
    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String(255),nullable=False)
    birth_date: Mapped[date] = mapped_column(Date,nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(String(255),nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    #*Relaciones
    created_businesses: Mapped[list["Business"]] = relationship(back_populates="creator")
    business_relationships: Mapped[list["UserBusiness"]] = relationship(back_populates="user")
    recoveries: Mapped[list["Recovery"]] = relationship(back_populates="user")
    created_movements: Mapped[list["Movement"]] = relationship(
        back_populates="creator",
        foreign_keys="Movement.created_by"
    )
    updated_movements: Mapped[list["Movement"]] = relationship(
        back_populates="updater",
        foreign_keys="Movement.updated_by"
    )
    created_sales: Mapped[list["Sale"]] = relationship(
        back_populates="creator",
        foreign_keys="Sale.created_by"
    )
    updated_sales: Mapped[list["Sale"]] = relationship(
        back_populates="updater",
        foreign_keys="Sale.updated_by"
    )
    imports: Mapped[list["Import"]] = relationship(back_populates="user")