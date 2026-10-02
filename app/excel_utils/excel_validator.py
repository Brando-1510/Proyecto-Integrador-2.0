import pandas as pd


class ExcelValidator:
    SALES_COLUMNS = [
        "Fecha",
        "Producto/Servicio",
        "Categoría",
        "Cantidad",
        "Precio Unitario",
        "Total",
    ]
    MOVEMENTS_COLUMNS = [
        "Fecha",
        "Tipo",
        "Categoría",
        "Descripción",
        "Monto",
        "Método de Pago",
    ]
    VALID_MOVEMENT_TYPES = {"Ingreso", "Gasto"}
    def validate(self, sales_df, movements_df):
        errors = []
        errors.extend(
            self.validate_columns(
                sales_df,
                self.SALES_COLUMNS,
                "Ventas"
            )
        )
        errors.extend(
            self.validate_columns(
                movements_df,
                self.MOVEMENTS_COLUMNS,
                "Movimientos"
            )
        )
        if errors:
            return errors
        errors.extend(self.validate_sales(sales_df))
        errors.extend(self.validate_movements(movements_df))
        return errors
    def validate_columns(self, df, required_columns, sheet_name):
        errors = []
        columns = [
            str(column).strip()
            for column in df.columns
        ]
        duplicated_columns = {
            column
            for column in columns
            if columns.count(column) > 1
        }
        if duplicated_columns:
            errors.append(
                f"Hoja '{sheet_name}': hay columnas duplicadas: "
                f"{', '.join(sorted(duplicated_columns))}."
            )
        missing_columns = [
            column
            for column in required_columns
            if column not in columns
        ]
        if missing_columns:
            errors.append(
                f"Hoja '{sheet_name}': faltan las columnas: "
                f"{', '.join(missing_columns)}."
            )
        return errors
    def _is_empty_row(self, row: pd.Series) -> bool:
        return all(pd.isna(value) or str(value).strip() == ""for value in row)
    def validate_sales(self, df):
        errors = []
        for index, row in df.iterrows():
            row_number = index + 4
            # Ignorar filas completamente vacías
            if self._is_empty_row(row):
                continue
            date = pd.to_datetime(row["Fecha"],errors="coerce")
            if pd.isna(date):
                errors.append(f"Ventas, fila {row_number}: la fecha no es válida.")
            product = str(row["Producto/Servicio"]).strip()
            if not product or product.lower() == "nan":
                errors.append(f"Ventas, fila {row_number}: el producto/servicio es obligatorio.")
            category = str(row["Categoría"]).strip()
            if not category or category.lower() == "nan":
                errors.append(f"Ventas, fila {row_number}: la categoría es obligatoria.")
            quantity = pd.to_numeric(row["Cantidad"],errors="coerce")
            if pd.isna(quantity) or quantity <= 0:
                errors.append(f"Ventas, fila {row_number}: la cantidad debe ser un número mayor que cero.")
            price = pd.to_numeric(row["Precio Unitario"],errors="coerce")
            if pd.isna(price) or price < 0:
                errors.append(f"Ventas, fila {row_number}: el precio unitario no es válido.")
            total = pd.to_numeric(row["Total"],errors="coerce")
            if pd.isna(total) or total < 0:
                errors.append(f"Ventas, fila {row_number}: el total no es válido.")
            if (
                not pd.isna(quantity) and not pd.isna(price) and not pd.isna(total)
            ):
                expected_total = quantity * price
                if round(total, 2) != round(expected_total, 2):
                    errors.append(
                        f"Ventas, fila {row_number}: el total no coincide con cantidad × precio unitario."
                    )
        return errors
    def validate_movements(self, df):
        errors = []
        for index, row in df.iterrows():
            row_number = index + 2
            # Ignorar filas completamente vacías
            if self._is_empty_row(row):
                continue
            date = pd.to_datetime(row["Fecha"],errors="coerce")
            if pd.isna(date):
                errors.append(f"Movimientos, fila {row_number}: la fecha no es válida.")
            movement_type = str(row["Tipo"]).strip()
            if movement_type not in self.VALID_MOVEMENT_TYPES:
                errors.append(
                    f"Movimientos, fila {row_number}: tipo de movimiento inválido: '{movement_type}'.")
            category = str(row["Categoría"]).strip()
            if not category or category.lower() == "nan":
                errors.append(f"Movimientos, fila {row_number}: la categoría es obligatoria.")
            description = str(row["Descripción"]).strip()
            if not description or description.lower() == "nan":
                errors.append(f"Movimientos, fila {row_number}: la descripción es obligatoria.")
            amount = pd.to_numeric(row["Monto"],errors="coerce")
            if pd.isna(amount) or amount <= 0:
                errors.append(f"Movimientos, fila {row_number}: el monto debe ser un número mayor que cero.")
            payment_method = str(row["Método de Pago"]).strip()
            if not payment_method or payment_method.lower() == "nan":
                errors.append(f"Movimientos, fila {row_number}: el método de pago es obligatorio.")
        return errors