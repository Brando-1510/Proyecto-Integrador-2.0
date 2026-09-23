from typing import Annotated, TYPE_CHECKING
from sqlalchemy import ForeignKey,String,Boolean,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.sale import Sale

class Category(Base):
    __tablename__ = "categories"
    category_id: Mapped[intpk]
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.business_id"),nullable=False)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    business: Mapped["Business"] = relationship(back_populates="categories")
    sales: Mapped[list["Sale"]] = relationship(back_populates="category")
    __table_args__ = (
        UniqueConstraint(
            "business_id",
            "name",
            name="uq_category_business_name"
        ),
    )