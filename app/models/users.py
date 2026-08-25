from typing_extensions import Annotated
from typing import List,Optional
from datetime import datetime
from sqlalchemy import ForeignKey,String,func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

# set up mapped_column() overrides, using whole column styles that are expected to be used in multiple places
intpk = Annotated[int, mapped_column(primary_key=True)]

class Users(Base):
    __tablename__="Users"
    user_id: Mapped[intpk]
    username: Mapped[str]=mapped_column(String(150),nullable=False)
    email: Mapped[str]=mapped_column(String(150),unique=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    # Se genera al insertar y se actualiza automáticamente en cada UPDATE
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(),onupdate=func.now())