import math
#*Esta clase contiene las funciones que comparan valores de períodos diferentes
class ComparisonFunctions:
    #*Calcula la variacion porcentual entre dos valores
    @staticmethod
    def calculate_percentage_variation(current_value: int | float,previous_value: int | float) -> float | None:
        if previous_value == 0:
            return None
        variation = ((current_value - previous_value) / previous_value) * 100
        return round(variation, 2)
    #*Analiza la variación de un indicador financiero.
    @staticmethod
    def _analyze_variation(
        current_value: int | float,previous_value: int | float,threshold: int | float
    ) -> dict:
        if threshold < 0:
            raise ValueError("El umbral no puede ser negativo.")
        if not math.isfinite(current_value) or not math.isfinite(previous_value):
            raise ValueError("Los valores deben ser números finitos.")
        percentage_variation = (
            ComparisonFunctions.calculate_percentage_variation(
                current_value,previous_value
            )
        )
        absolute_variation = current_value - previous_value
        if absolute_variation > 0:
            direction = "Aumento"
        elif absolute_variation < 0:
            direction = "Disminución"
        else:
            direction = "Sin cambio"
        is_relevant = (abs(percentage_variation) >= threshold
            if percentage_variation is not None
            else None
        )
        return {
            "current_value": current_value,
            "previous_value": previous_value,
            "absolute_variation": round(absolute_variation, 2),
            "percentage_variation": percentage_variation,
            "direction": direction,
            "is_relevant": is_relevant
        }
    #*Analiza los cambios en los gastos
    @staticmethod
    def analyze_expense_variation(
        current_value: int | float,previous_value: int | float,threshold: int | float = 10
    ) -> dict:
        return ComparisonFunctions._analyze_variation(
            current_value,
            previous_value,
            threshold
        )
    #*Analiza los cambios en los ingresos
    @staticmethod
    def analyze_income_variation(
        current_value: int | float,previous_value: int | float,threshold: int | float = 10
    ) -> dict:
        return ComparisonFunctions._analyze_variation(
            current_value,
            previous_value,
            threshold
        )
    #*Compara balances financieros
    @staticmethod
    def analyze_balance_variation(
        current_value: int | float,previous_value: int | float,threshold: int | float = 10
    ) -> dict:
        if threshold < 0:
            raise ValueError("El umbral no puede ser negativo.")
        if not math.isfinite(current_value) or not math.isfinite(previous_value):
            raise ValueError("Los valores deben ser números finitos.")
        absolute_variation = current_value - previous_value
        if absolute_variation > 0:
            direction = "Mejora"
        elif absolute_variation < 0:
            direction = "Empeora"
        else:
            direction = "Sin cambio"
        # El porcentaje convencional solo se calcula cuando el balance anterior es positivo.
        percentage_variation = (
            ComparisonFunctions.calculate_percentage_variation(
                current_value,previous_value
            )
            if previous_value > 0
            else None
        )
        is_relevant = (abs(percentage_variation) >= threshold
            if percentage_variation is not None
            else None
        )
        return {
            "current_value": current_value,
            "previous_value": previous_value,
            "absolute_variation": round(absolute_variation, 2),
            "percentage_variation": percentage_variation,
            "direction": direction,
            "is_relevant": is_relevant,
            "changed_sign": (
                current_value * previous_value < 0
            )
        }
