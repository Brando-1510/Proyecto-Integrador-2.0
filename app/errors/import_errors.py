from dataclasses import dataclass
from enum import Enum

class ImportErrorType(Enum):
    """
    Tipos de errores que pueden ocurrir
    durante la importación o guardado.
    """
    FILE_ALREADY_EXISTS = "file_already_exists"
    CATEGORY_NOT_FOUND = "category_not_found"
    INVALID_FILE = "invalid_file"
    INVALID_DATA = "invalid_data"
    DATABASE_ERROR = "database_error"
    UNKNOWN = "unknown"


@dataclass
class ImportErrorResult:
    """
    Representa un error ocurrido durante
    la importación o guardado.
    """
    error_type: ImportErrorType
    # Mensaje que puede mostrarse al usuario
    message: str
    # Mensaje técnico para debugging/logging
    technical_message: str | None = None