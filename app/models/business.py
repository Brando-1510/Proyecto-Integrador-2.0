from typing_extensions import Annotated
from typing import List,Optional
from datetime import datetime
from sqlalchemy import ForeignKey,String,func,Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base
from users import Users

# set up mapped_column() overrides, using whole column styles that are expected to be used in multiple places
intpk = Annotated[int, mapped_column(primary_key=True)]

class Business(Base):
    __tablename__="Bussiness"
    business_id: Mapped[intpk]
    business_name: Mapped[str]=mapped_column(String(150),nullable=False)
    type_of_business:Mapped[str]=mapped_column(String(150),nullable=False)
    start_of_operations: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    owner=Mapped[int]=mapped_column(ForeignKey("Users.user_id"),nullable=False,unique=True)
    description:Mapped[str] = mapped_column(Text)
    # Se genera al insertar y se actualiza automáticamente en cada UPDATE
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())