import pandas as pd
from dataclasses import dataclass, field
from app.errors.import_errors import ImportErrorResult

@dataclass
class ExcelImportResult:
    #*Resultado del procesamiento de un archivo Excel
    success: bool = False
    sales: pd.DataFrame | None = None
    movements: pd.DataFrame | None = None
    errors: list[ImportErrorResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
