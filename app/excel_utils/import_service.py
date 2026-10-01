from typing import Callable, Optional
from app.excel_utils.excel_reader import ExcelReader
from app.excel_utils.excel_validator import ExcelValidator
from app.excel_utils.excel_transformer import ExcelTransformer
from app.excel_utils.excel_result import ExcelImportResult

class ImportService:
    def __init__(self):
        self.reader = ExcelReader()
        self.validator = ExcelValidator()
        self.transformer = ExcelTransformer()
    def process_excel(self,path: str,
    progress_callback: Optional[Callable[[int, str], None]] = None) -> ExcelImportResult:
        def notify(percentage: int, message: str):
            if progress_callback:
                progress_callback(percentage, message)
        #*Leer Excel
        notify(10, "Leyendo archivo Excel...")
        data = self.reader.read(path)
        if data is None:
            return ExcelImportResult(
                success=False,
                errors=[
                    "No se pudo leer el archivo Excel."
                ]
            )
        sales_df, movements_df = data
        errors = self.validator.validate(
            sales_df,
            movements_df
        )
        #*Normalizar
        notify(30, "Normalizando formato de datos...")
        sales_df, movements_df = (
            self.transformer.normalize_excel(
                sales_df,
                movements_df
            )
        )
        #*Validar
        notify(50, "Validando datos...")
        errors = self.validator.validate(sales_df, movements_df)
        if errors:
            return ExcelImportResult(success=False, errors=errors)
        #*Transformar tipos
        notify(80, "Transformando tipos de datos...")
        sales_df, movements_df = (
            self.transformer.transform_excel(
                sales_df,
                movements_df
            )
        )
        #*Devolver resultado
        notify(100, "Procesamiento completado.")
        return ExcelImportResult(
            success=True,
            sales=sales_df,
            movements=movements_df
        )