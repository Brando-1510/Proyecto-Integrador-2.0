from typing import Annotated,TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, String, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.users import Users
    from app.models.user_business import UserBusiness
class Business(Base):
    __tablename__ = "businesses"
    business_id: Mapped[intpk]
    business_name: Mapped[str] = mapped_column(String(150),nullable=False)
    type_of_business: Mapped[str] = mapped_column(String(150),nullable=False)
    start_of_operations: Mapped[datetime | None]
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False,unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())
    owner: Mapped["Users"] = relationship(back_populates="owned_business")
    user_relationships: Mapped[list["UserBusiness"]] = relationship(back_populates="business")