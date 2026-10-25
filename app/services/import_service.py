from app.models.imports import Import
from app.repositories.import_repository import ImportRepository
from app.utils.hash_utils import calculate_sha256
from app.errors.import_errors import DuplicateImportError

class ImportService:
    def save_import(
        self,user_id: int,business_id: int,file_path: str,file_name: str,session,
    ):
        import_repository = ImportRepository(session)
        file_hash = calculate_sha256(file_path)
        existing_import = (
            import_repository.get_by_business_and_hash(business_id,file_hash,)
        )
        if existing_import:
            raise DuplicateImportError("El archivo que intenta registrar ya existe en la base de datos.")
        import_obj = Import(
            user_id=user_id,
            business_id=business_id,
            file_name=file_name,
            file_hash=file_hash,
        )
        return import_repository.create(import_obj)
