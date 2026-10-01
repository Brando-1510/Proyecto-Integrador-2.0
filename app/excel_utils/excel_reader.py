import pandas as pd
from pathlib import Path
class ExcelReader:
    REQUIRED_SHEETS = [
        "Ventas",
        "Movimientos",
    ]
    def read(self,path: str) -> tuple[pd.DataFrame, pd.DataFrame] | None:
        # Verificar que se haya proporcionado una ruta
        if not path:
            return None
        file_path = Path(path)
        # Verificar que el archivo exista
        if not file_path.is_file():
            return None
        # Verificar que sea un archivo .xlsx
        if file_path.suffix.lower() != ".xlsx":
            return None
        try:
            with pd.ExcelFile(file_path,engine="openpyxl") as excel:
                # Verificar que existan las hojas requeridas
                for sheet in self.REQUIRED_SHEETS:
                    if sheet not in excel.sheet_names:
                        return None
                # Leer las hojas
                sales_df = pd.read_excel(excel,sheet_name="Ventas",header=2)
                movements_df = pd.read_excel(excel,sheet_name="Movimientos",header=2)
                return sales_df, movements_df
        except Exception as e:
            print("ERROR REAL AL LEER EXCEL:", repr(e))
            return None
