from datetime import datetime
from typing import Annotated, TYPE_CHECKING
from sqlalchemy import ForeignKey, String,func,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.users import Users
    from app.models.business import Business
    from app.models.movement import Movement
    from app.models.sale import Sale

class Import(Base):
    __tablename__ = "imports"
    import_id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.business_id"),nullable=False)
    file_name: Mapped[str] = mapped_column(String(255),nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64),nullable=False)
    imported_at: Mapped[datetime] = mapped_column(nullable=False,server_default=func.now())
    user: Mapped["Users"] = relationship(back_populates="imports")
    business: Mapped["Business"] = relationship(back_populates="imports")
    movements: Mapped[list["Movement"]] = relationship(back_populates="import_record")
    sales: Mapped[list["Sale"]] = relationship(back_populates="import_record")
    __table_args__ = (
        UniqueConstraint("business_id","file_hash",name="uq_import_business_hash"),
    )