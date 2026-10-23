import re
import unicodedata
import pandas as pd

class ExcelTransformer:
    SALES_COLUMNS = {
        "fecha": "Fecha",
        "producto/servicio": "Producto/Servicio",
        "categoria": "Categoría",
        "cantidad": "Cantidad",
        "precio unitario": "Precio Unitario",
        "precio unitario ($)": "Precio Unitario",
        "total": "Total",
        "total ($)": "Total",
    }
    MOVEMENTS_COLUMNS = {
        "fecha": "Fecha",
        "tipo": "Tipo",
        "categoria": "Categoría",
        "descripcion": "Descripción",
        "monto": "Monto",
        "monto ($)": "Monto",
        "metodo de pago": "Método de Pago",
    }
    def normalize_excel(self,sales_df: pd.DataFrame | None,movements_df: pd.DataFrame | None,) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
        if sales_df is not None:
            sales_df = self._normalize_columns(sales_df, self.SALES_COLUMNS)
            sales_df = self._clean_text(sales_df)
            if sales_df.empty:
                sales_df = None

        if movements_df is not None:
            movements_df = self._normalize_columns(movements_df, self.MOVEMENTS_COLUMNS)
            movements_df = self._clean_text(movements_df)
            if movements_df.empty:
                movements_df = None
        return sales_df, movements_df
    def transform_excel(
        self,sales_df: pd.DataFrame | None,movements_df: pd.DataFrame | None,
    ) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
        if sales_df is not None:
            sales_df = self._transform_sales(sales_df)
        if movements_df is not None:
            movements_df = self._transform_movements(movements_df)
        return sales_df, movements_df

    @staticmethod
    def _normalize_header_key(column: object) -> str:
        value = str(column).strip().casefold()
        # Eliminar tildes para reconocer variantes de encabezados.
        value = unicodedata.normalize("NFKD", value)
        value = "".join(
            char for char in value
            if not unicodedata.combining(char)
        )
        # Unificar espacios y espacios alrededor de "/".
        value = re.sub(r"\s*/\s*", "/", value)
        value = re.sub(r"\s+", " ", value)
        return value

    def _normalize_columns(self,df: pd.DataFrame,column_mapping: dict[str, str],) -> pd.DataFrame:
        df = df.copy()
        # Normalizar también las claves del diccionario.
        normalized_mapping = {
            self._normalize_header_key(key): value
            for key, value in column_mapping.items()
        }
        df.columns = [
            normalized_mapping.get(
                self._normalize_header_key(column),
                str(column).strip(),
            )
            for column in df.columns
        ]
        return df

    @staticmethod
    def _clean_text(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        text_columns = df.select_dtypes(include=["object", "string"]).columns
        for column in text_columns:
            def clean_value(value):
                if not isinstance(value, str):
                    return value
                value = value.strip()
                return value if value else pd.NA
            df[column] = df[column].map(clean_value)
        # Eliminar filas completamente vacías sin reiniciar índices.
        df = df.dropna(how="all")
        return df

    @staticmethod
    def _transform_sales(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Cantidad"] = pd.to_numeric(df["Cantidad"])
        df["Precio Unitario"] = pd.to_numeric(df["Precio Unitario"])
        df["Total"] = pd.to_numeric(df["Total"])
        return df

    @staticmethod
    def _transform_movements(df: pd.DataFrame,) -> pd.DataFrame:
        df = df.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Tipo"] = df["Tipo"].map(
            lambda value: (
                value.strip().capitalize()
                if isinstance(value, str)
                else value
            )
        )
        df["Monto"] = pd.to_numeric(df["Monto"])
        return df
