from sqlalchemy import select
from app.models.imports import Import

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