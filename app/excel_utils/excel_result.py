import pandas as pd
from dataclasses import dataclass, field


@dataclass
class ExcelImportResult:
    success: bool = False

    sales: pd.DataFrame | None = None
    movements: pd.DataFrame | None = None

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)