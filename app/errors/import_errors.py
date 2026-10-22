from dataclasses import dataclass
from enum import Enum

class ImportErrorType(Enum):
    #*Clasificación de errores de importación y guardado.
    FILE_ALREADY_EXISTS = "file_already_exists"
    CATEGORY_NOT_FOUND = "category_not_found"
    INVALID_FILE = "invalid_file"
    INVALID_DATA = "invalid_data"
    DATABASE_ERROR = "database_error"
    UNKNOWN = "unknown"

@dataclass
class ImportErrorResult:
    #*Representa un error individual del proceso de importación
    error_type: ImportErrorType
    message: str
    technical_message: str | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    column_name: str | None = None