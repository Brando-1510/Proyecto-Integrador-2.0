from sqlalchemy import select
from app.models.imports import Import
from app.models.users import Users
from datetime import date

class ImportRepository:
    def __init__(self, session):
        self.session = session

    def create(self, import_obj: Import):
        self.session.add(import_obj)
        self.session.flush()
        return import_obj
    def get_by_business_and_hash(self,business_id: int,file_hash: str):
        stmt = select(Import).where(
            Import.business_id == business_id,
            Import.file_hash == file_hash
        )
        return self.session.scalar(stmt)
    def get_imports(self,business_id:int,start_date:date,end_date:date,name:str | None=None):
        stmt=(
            select(
                Import.import_id,Import.file_name,Import.imported_at,Users.username
            )
            .join(
                Users,(Import.user_id==Users.user_id)
            )
            .where(
                Import.business_id==business_id,
                Import.imported_at.between(start_date,end_date)
            )
        )
        if name is not None:
            stmt=stmt.where(Users.username==name)
        resultado = self.session.execute(stmt).all()
        return resultado