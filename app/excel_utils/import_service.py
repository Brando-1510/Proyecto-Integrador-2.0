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
        if sales_df is None and movements_df is None:
            return ExcelImportResult(
                success=False,
                errors=[
                    ImportErrorResult(
                        error_type=ImportErrorType.INVALID_DATA,
                        message=(
                            "El archivo no contiene datos procesables en las hojas "
                            "'Ventas' o 'Movimientos'."
                        ),
                    )
                ],
            )
        # Validar los datos normalizados.
        notify(50, "Validando datos...")
        errors = self.validator.validate(sales_df, movements_df)
        if errors:
            notify(100, "Se encontraron errores en el archivo.")
            return ExcelImportResult(success=False,errors=errors,)
        # Convertir los datos validados.
        notify(70, "Preparando los datos...")
        try:
            sales_df, movements_df = self.transformer.transform_excel(sales_df,movements_df,)
        except (ValueError, TypeError, KeyError, OverflowError) as e:
            return ExcelImportResult(
                success=False,
                errors=[
                    ImportErrorResult(
                        error_type=ImportErrorType.INVALID_DATA,
                        message=(
                            "No fue posible convertir los datos del archivo. "
                            "Revisa las fechas y los valores numéricos."
                        ),
                        technical_message=str(e),
                    )
                ],
            )
        notify(100, "Procesamiento completado.")
        return ExcelImportResult(
            success=True,
            sales=sales_df,
            movements=movements_df,
        )
