import pandas as pd

class ExcelTransformer:
    SALES_COLUMNS = {
        "fecha": "Fecha",
        "producto/servicio": "Producto/Servicio",
        "categoría": "Categoría",
        "cantidad": "Cantidad",
        "precio unitario": "Precio Unitario",
        "total": "Total",
    }
    MOVEMENTS_COLUMNS = {
        "fecha": "Fecha",
        "tipo": "Tipo",
        "categoría": "Categoría",
        "descripción": "Descripción",
        "monto": "Monto",
        "método de pago": "Método de Pago",
    }
    def normalize_excel(self,sales_df: pd.DataFrame,movements_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        sales_df = self._normalize_columns(sales_df,self.SALES_COLUMNS)
        movements_df = self._normalize_columns(movements_df,self.MOVEMENTS_COLUMNS)
        sales_df = self._clean_text(sales_df)
        movements_df = self._clean_text(movements_df)
        return sales_df, movements_df
    def transform_excel(self,sales_df: pd.DataFrame,movements_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        sales_df = self._transform_sales(sales_df)
        movements_df = self._transform_movements(movements_df)
        return sales_df, movements_df
    def _normalize_columns(self,df: pd.DataFrame,column_mapping: dict[str, str]) -> pd.DataFrame:
        df = df.copy()
        df.columns = [
            column_mapping.get(
                str(column).strip().casefold(),
                str(column).strip()
            )
            for column in df.columns
        ]
        return df
    def _clean_text(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for column in df.select_dtypes(
            include=["object", "string"]
        ).columns:
            df[column] = df[column].map(
                lambda value: (
                    value.strip()
                    if isinstance(value, str)
                    else value
                )
            )
        return df
    def _transform_sales(self,df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Cantidad"] = pd.to_numeric(df["Cantidad"])
        df["Precio Unitario"] = pd.to_numeric(df["Precio Unitario"])
        df["Total"] = pd.to_numeric(df["Total"])
        return df
    def _transform_movements(self,df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Tipo"] = (df["Tipo"].str.strip().str.capitalize())
        df["Monto"] = pd.to_numeric(df["Monto"])
        return df