from app.excel_utils.excel_reader import ExcelReader
from app.excel_utils.excel_validator import ExcelValidator
from app.excel_utils.excel_transformer import ExcelTransformer
from app.excel_utils.excel_result import ExcelImportResult

class ImportService:
    def __init__(self):
        self.reader = ExcelReader()
        self.validator = ExcelValidator()
        self.transformer = ExcelTransformer()
    def process_excel(self,path: str) -> ExcelImportResult:
        #*Leer Excel
        data = self.reader.read(path)
        if data is None:
            return ExcelImportResult(
                success=False,
                errors=[
                    "No se pudo leer el archivo Excel."
                ]
            )
        sales_df, movements_df = data
        #*Normalizar
        sales_df, movements_df = (
            self.transformer.normalize_excel(
                sales_df,
                movements_df
            )
        )
        #*Validar
        errors = self.validator.validate(sales_df,movements_df)
        if errors:
            return ExcelImportResult(success=False,errors=errors)
        #*Transformar tipos
        sales_df, movements_df = (
            self.transformer.transform_excel(
                sales_df,
                movements_df
            )
        )
        #*Devolver resultado
        return ExcelImportResult(
            success=True,
            sales=sales_df,
            movements=movements_df
        )