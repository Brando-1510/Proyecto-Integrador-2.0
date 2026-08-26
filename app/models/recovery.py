from typing import Annotated,TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, String, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.users import Users
class Recovery(Base):
    __tablename__ = "recoveries"
    recovery_id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    codigo: Mapped[str] = mapped_column(String(255),nullable=False)
    token: Mapped[str] = mapped_column(String(255),nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    used: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["Users"] = relationship(back_populates="recoveries")