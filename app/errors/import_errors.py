from dataclasses import dataclass
from enum import Enum

class ImportErrorType(Enum):
    FILE_ALREADY_EXISTS = "file_already_exists"
    CATEGORY_NOT_FOUND = "category_not_found"
    INVALID_FILE = "invalid_file"
    INVALID_DATA = "invalid_data"
    DATABASE_ERROR = "database_error"
    UNKNOWN = "unknown"

@dataclass
class ImportErrorResult:
    error_type: ImportErrorType
    message: str
    technical_message: str | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    column_name: str | None = None
    missing_categories: list[str] | None = None


class DuplicateImportError(Exception):
    #*El archivo ya fue importado para este negocio.
    pass

class CategoryNotFoundError(Exception):
    #*Una o más categorías de ventas no existen para el negocio
    def __init__(self, missing_categories: list[str]):
        self.missing_categories = missing_categories
        message = (
            "Faltan las siguientes categorías de ventas: "
            + ", ".join(missing_categories)
        )
        super().__init__(message)