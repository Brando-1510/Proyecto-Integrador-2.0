from typing_extensions import Annotated
from typing import List,Optional
from datetime import datetime
from sqlalchemy import ForeignKey,String,func,Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base

# set up mapped_column() overrides, using whole column styles that are expected to be used in multiple places
intpk = Annotated[int, mapped_column(primary_key=True)]

class Recovery(Base):
    __tablename__="Recovery"
    recovery_id: Mapped[intpk]
    