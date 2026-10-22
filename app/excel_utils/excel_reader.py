import logging
from pathlib import Path
import pandas as pd
logger = logging.getLogger(__name__)

class ExcelReader:
    REQUIRED_SHEETS = ("Ventas", "Movimientos")
    def read(self, path: str) -> dict[str, pd.DataFrame | None] | None:
        """
        Lee las hojas disponibles del archivo Excel.
        Retorna None si la ruta, el archivo o la lectura son
        inválidos. Las hojas ausentes o vacías se representan
        con None.
        """
        if not path:
            return None
        file_path = Path(path)
        if not file_path.is_file():
            return None
        if file_path.suffix.lower() != ".xlsx":
            return None
        try:
            with pd.ExcelFile(file_path, engine="openpyxl") as excel:
                result = {
                    sheet: None
                    for sheet in self.REQUIRED_SHEETS
                }
                for sheet in self.REQUIRED_SHEETS:
                    if sheet not in excel.sheet_names:
                        continue
                    df = pd.read_excel(
                        excel,
                        sheet_name=sheet,
                        header=2,
                    )
                    # Ignorar filas completamente vacías.
                    df = df.dropna(how="all")
                    if df.empty:
                        continue
                    result[sheet] = df
                return result
        except Exception:
            logger.exception(
                "No se pudo leer el archivo Excel: %s",file_path,
            )
            return None
