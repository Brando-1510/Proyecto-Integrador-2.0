from app.models.imports import Import
from app.utils.hash_utils import calculate_sha256

class ImportService:
    def __init__(self,import_repository):
        self.import_repository=import_repository
    def save_import(self,user_id,business_id,file_path,file_name):
        hash_256=calculate_sha256(file_path)
        if self.import_repository.get_by_business_and_hash(business_id,hash_256):
            raise ValueError("El archivo que intenta registrar ya existe en la base de datos")
        import_obj= Import(
            user_id=user_id,
            business_id=business_id,
            file_name=file_name,
            file_hash=hash_256
        )
        import_created=self.import_repository.create(import_obj)
        return import_created