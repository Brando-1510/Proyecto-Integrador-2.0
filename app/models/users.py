from typing import Annotated,TYPE_CHECKING
from datetime import datetime,date
from sqlalchemy import String, func,Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

# Tipo reutilizable para claves primarias
intpk = Annotated[int, mapped_column(primary_key=True)]

if TYPE_CHECKING:
    from app.models.recovery import Recovery
    from app.models.business import Business
    from app.models.user_business import UserBusiness
class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String(150),nullable=False)
    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String(255),nullable=False)
    birth_date:Mapped[date]=mapped_column(Date,nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    # Recuperaciones de contraseña
    recoveries: Mapped[list["Recovery"]] = relationship(back_populates="user")
    # Negocio del cual es propietario
    owned_business: Mapped["Business | None"] = relationship(back_populates="owner")
    # Negocios a los que está asociado
    business_relationships: Mapped[list["UserBusiness"]] = relationship(back_populates="user")