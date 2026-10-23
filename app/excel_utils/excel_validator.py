import pandas as pd
from app.errors.import_errors import ImportErrorResult, ImportErrorType
from app.utils.date_utils import DateUtils
from app.models.movement import MovementType,PaymentMethod,IncomeCategory,ExpenseCategory


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
    VALID_MOVEMENT_TYPES = {item.value.casefold() for item in MovementType}
    VALID_PAYMENT_METHODS = {item.value.casefold() for item in PaymentMethod}
    VALID_INCOME_CATEGORIES = {item.value.casefold() for item in IncomeCategory}
    VALID_EXPENSE_CATEGORIES = {item.value.casefold() for item in ExpenseCategory}

    def validate(self, sales_df: pd.DataFrame | None, movements_df: pd.DataFrame | None) -> list[ImportErrorResult]:
        errors: list[ImportErrorResult] = []
        if sales_df is not None:
            errors.extend(self.validate_columns(sales_df, self.SALES_COLUMNS, "Ventas"))
        if movements_df is not None:
            errors.extend(self.validate_columns(movements_df, self.MOVEMENTS_COLUMNS, "Movimientos"))
        if errors:
            return errors
        if sales_df is not None:
            errors.extend(self.validate_sales(sales_df))
        if movements_df is not None:
            errors.extend(self.validate_movements(movements_df))
        return errors
    @staticmethod
    def _build_error(
        message: str,
        error_type: ImportErrorType,
        sheet_name: str | None = None,
        row_number: int | None = None,
        column_name: str | None = None,
    ) -> ImportErrorResult:
        return ImportErrorResult(
            error_type=error_type,
            message=message,
            sheet_name=sheet_name,
            row_number=row_number,
            column_name=column_name,
        )
    def validate_columns(
        self, df: pd.DataFrame, required_columns: list[str], sheet_name: str
    ) -> list[ImportErrorResult]:
        errors: list[ImportErrorResult] = []
        columns = [" ".join(str(column).split()) for column in df.columns]
        duplicated_columns = {column for column in columns if columns.count(column) > 1}
        if duplicated_columns:
            duplicated = ", ".join(sorted(duplicated_columns))
            errors.append(
                self._build_error(
                    f"Hay columnas duplicadas: {duplicated}.",
                    ImportErrorType.INVALID_FILE,
                    sheet_name=sheet_name,
                )
            )
        missing_columns = [column for column in required_columns if column not in columns]
        if missing_columns:
            missing = ", ".join(missing_columns)
            errors.append(
                self._build_error(
                    f"Faltan las columnas obligatorias: {missing}.",
                    ImportErrorType.INVALID_FILE,
                    sheet_name=sheet_name,
                )
            )
        return errors
    @staticmethod
    def _is_empty_row(row: pd.Series) -> bool:
        return all(
            pd.isna(value) or (isinstance(value, str) and not value.strip())
            for value in row
        )
    @staticmethod
    def _is_missing(value) -> bool:
        if pd.isna(value):
            return True
        return isinstance(value, str) and not value.strip()
    @staticmethod
    def _is_positive_number(value) -> bool:
        number = pd.to_numeric(value, errors="coerce")
        return bool(pd.notna(number) and number > 0)
    def _validate_date(self, value, sheet_name: str, row_number: int) -> list[ImportErrorResult]:
        date_value = pd.to_datetime(value, errors="coerce")
        if pd.isna(date_value):
            return [
                self._build_error("La fecha no es válida.", ImportErrorType.INVALID_DATA, sheet_name, row_number, "Fecha")
            ]
        if DateUtils.identify_future_date(date_value.date()):
            return [
                self._build_error("La fecha no puede ser futura.", ImportErrorType.INVALID_DATA, sheet_name, row_number, "Fecha")
            ]
        return []
    def validate_sales(self, df: pd.DataFrame) -> list[ImportErrorResult]:
        errors: list[ImportErrorResult] = []
        for index, row in df.iterrows():
            row_number = index + 4
            if self._is_empty_row(row):
                continue
            errors.extend(self._validate_date(row["Fecha"], "Ventas", row_number))
            if self._is_missing(row["Producto/Servicio"]):
                errors.append(
                    self._build_error(
                        "El producto/servicio es obligatorio.",
                        ImportErrorType.INVALID_DATA,
                        "Ventas", row_number, "Producto/Servicio",
                    )
                )
            if self._is_missing(row["Categoría"]):
                errors.append(
                    self._build_error(
                        "La categoría es obligatoria.",
                        ImportErrorType.INVALID_DATA,
                        "Ventas", row_number, "Categoría",
                    )
                )
            quantity = pd.to_numeric(row["Cantidad"], errors="coerce")
            price = pd.to_numeric(row["Precio Unitario"], errors="coerce")
            total = pd.to_numeric(row["Total"], errors="coerce")
            if not self._is_positive_number(quantity):
                errors.append(
                    self._build_error(
                        "La cantidad debe ser un número mayor que cero.",
                        ImportErrorType.INVALID_DATA,
                        "Ventas", row_number, "Cantidad",
                    )
                )
            if not self._is_positive_number(price):
                errors.append(
                    self._build_error(
                        "El precio unitario debe ser un número mayor que cero.",
                        ImportErrorType.INVALID_DATA,
                        "Ventas", row_number, "Precio Unitario",
                    )
                )
            if not self._is_positive_number(total):
                errors.append(
                    self._build_error(
                        "El total debe ser un número mayor que cero.",
                        ImportErrorType.INVALID_DATA,
                        "Ventas", row_number, "Total",
                    )
                )
            if (
                self._is_positive_number(quantity)
                and self._is_positive_number(price)
                and self._is_positive_number(total)
            ):
                expected_total = quantity * price
                if round(float(total), 2) != round(float(expected_total), 2):
                    errors.append(
                        self._build_error(
                            "El total no coincide con cantidad × precio unitario.",
                            ImportErrorType.INVALID_DATA,
                            "Ventas", row_number, "Total",
                        )
                    )
        return errors
    def validate_movements(self, df: pd.DataFrame) -> list[ImportErrorResult]:
        errors: list[ImportErrorResult] = []
        for index, row in df.iterrows():
            row_number = index + 4
            if self._is_empty_row(row):
                continue
            errors.extend(self._validate_date(row["Fecha"], "Movimientos", row_number))
            movement_type = row["Tipo"]
            if (
                self._is_missing(movement_type)
                or str(movement_type).strip().casefold() not in self.VALID_MOVEMENT_TYPES
            ):
                errors.append(
                    self._build_error(
                        f"Tipo de movimiento inválido: '{movement_type}'.",
                        ImportErrorType.INVALID_DATA,
                        "Movimientos", row_number, "Tipo",
                    )
                )
                #*
            category = row["Categoría"]
            if self._is_missing(category):
                errors.append(
                    self._build_error(
                        "La categoría es obligatoria.",
                        ImportErrorType.INVALID_DATA,
                        "Movimientos", row_number, "Categoría",
                    )
                )
            else:
                movement_type_value = str(movement_type).strip().casefold()
                category_value = str(category).strip().casefold()
                if movement_type_value == MovementType.INCOME.value.casefold():
                    valid_categories = self.VALID_INCOME_CATEGORIES
                elif movement_type_value == MovementType.EXPENSE.value.casefold():
                    valid_categories = self.VALID_EXPENSE_CATEGORIES
                else:
                    valid_categories = None
                if (
                    valid_categories is not None
                    and category_value not in valid_categories
                ):
                    errors.append(
                        self._build_error(
                            f"La categoría '{category}' no es válida para "
                            f"el tipo de movimiento '{movement_type}'.",
                            ImportErrorType.INVALID_DATA,
                            "Movimientos", row_number, "Categoría",
                        )
                    )
            if self._is_missing(row["Descripción"]):
                errors.append(
                    self._build_error(
                        "La descripción es obligatoria.",
                        ImportErrorType.INVALID_DATA,
                        "Movimientos", row_number, "Descripción",
                    )
                )
            amount = pd.to_numeric(row["Monto"], errors="coerce")
            if not self._is_positive_number(amount):
                errors.append(
                    self._build_error(
                        "El monto debe ser un número mayor que cero.",
                        ImportErrorType.INVALID_DATA,
                        "Movimientos", row_number, "Monto",
                    )
                )
            payment_method = row["Método de Pago"]
            if (
                self._is_missing(payment_method)
                or str(payment_method).strip().casefold() not in self.VALID_PAYMENT_METHODS
            ):
                errors.append(
                    self._build_error(
                        f"Método de pago inválido: '{payment_method}'.",
                        ImportErrorType.INVALID_DATA,
                        "Movimientos", row_number, "Método de Pago",
                    )
                )
        return errors