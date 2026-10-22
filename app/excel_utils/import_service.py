from typing import Callable
from app.excel_utils.excel_reader import ExcelReader
from app.excel_utils.excel_validator import ExcelValidator
from app.excel_utils.excel_transformer import ExcelTransformer
from app.excel_utils.excel_result import ExcelImportResult
from app.errors.import_errors import ImportErrorResult, ImportErrorType


class ImportService:
    def __init__(self):
        self.reader = ExcelReader()
        self.validator = ExcelValidator()
        self.transformer = ExcelTransformer()
    def process_excel(
        self,path: str,progress_callback: Callable[[int, str], None] | None = None,
    ) -> ExcelImportResult:
        def notify(percentage: int, message: str):
            if progress_callback:
                progress_callback(percentage, message)
        # Leer las hojas disponibles.
        notify(10, "Leyendo archivo Excel...")
        data = self.reader.read(path)
        if data is None:
            return ExcelImportResult(
                success=False,
                errors=[
                    ImportErrorResult(
                        error_type=ImportErrorType.INVALID_FILE,
                        message="No se pudo leer el archivo Excel.",
                    )
                ],
            )
        sales_df = data["Ventas"]
        movements_df = data["Movimientos"]
        # Comprobar si existe información procesable.
        has_sales = sales_df is not None
        has_movements = movements_df is not None
        if not has_sales and not has_movements:
            return ExcelImportResult(
                success=False,
                errors=[
                    ImportErrorResult(
                        error_type=ImportErrorType.INVALID_DATA,
                        message=(
                            "El archivo no contiene datos en las hojas "
                            "'Ventas' o 'Movimientos'."
                        ),
                    )
                ],
            )
        # Normalizar encabezados y textos.
        notify(30, "Normalizando formato de datos...")
        sales_df, movements_df = self.transformer.normalize_excel(sales_df,movements_df,)
        # Validar los datos normalizados.
        notify(50, "Validando datos...")
        errors = self.validator.validate(sales_df, movements_df)
        if errors:
            return ExcelImportResult(
                success=False,
                errors=errors,
            )
        # Transformar los tipos de datos.
        notify(80, "Transformando tipos de datos...")
        sales_df, movements_df = self.transformer.transform_excel(sales_df,movements_df,)
        # Devolver únicamente las hojas que contenían datos.
        notify(100, "Procesamiento completado.")
        return ExcelImportResult(
            success=True,
            sales=sales_df if has_sales else None,
            movements=movements_df if has_movements else None,
        )
