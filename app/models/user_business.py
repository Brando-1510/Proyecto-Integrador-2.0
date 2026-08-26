from typing import Annotated,TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, func, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.users import Users
    from app.models.business import Business

class Role(Enum):
    ADMIN = "gerente"
    ASSISTANT_MANAGER = "asistente del gerente"
    ACCOUNTANT = "contador"
    EMPLOYEE = "empleado"

class UserBusiness(Base):
    __tablename__ = "user_business"
    user_business_id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.business_id"),nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role),default=Role.EMPLOYEE,nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    user: Mapped["Users"] = relationship(back_populates="business_relationships")
    business: Mapped["Business"] = relationship(back_populates="user_relationships")
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "business_id",
            name="uq_user_business"
        ),
    )