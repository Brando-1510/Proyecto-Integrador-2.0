from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from math import sqrt
from statistics import median
from typing import Any

class RecommendationFunctions:
    #Funciones de análisis para las recomendaciones financieras
    class Area(str, Enum):
        EXPENSES = "gastos"
        INCOME = "ingresos"
        SALES = "ventas"
    class Priority(str, Enum):
        HIGH = "alta"
        OPPORTUNITY = "oportunidad"
        INFORMATIONAL = "informativa"

    #*Constantes de las reglas
    # G-01
    EXPENSE_GROWTH_THRESHOLD = Decimal("50")
    EXPENSE_MIN_PREVIOUS_SHARE = Decimal("10")
    # G-02
    EXPENSE_INCOME_RATIO_THRESHOLD = Decimal("1.20")
    IMBALANCE_MIN_HISTORICAL_SHARE = Decimal("5")
    # V-01
    SALES_DROP_THRESHOLD = Decimal("-40")
    SALES_DROP_MIN_HISTORICAL_SHARE = Decimal("10")
    # V-02
    PRODUCT_SALES_GROWTH_THRESHOLD = Decimal("30")
    PRODUCT_MIN_PREVIOUS_SHARE = Decimal("5")
    # V-04
    PRODUCT_QUANTITY_GROWTH_THRESHOLD = Decimal("30")
    # V-06
    SALES_CV_THRESHOLD = Decimal("50")
    MIN_ACTIVE_SALES_DAYS = 15
    # I-04
    MIN_PERIODIC_INCOMES = 3
    MIN_INCOME_INTERVAL_DAYS = 25
    MAX_INCOME_INTERVAL_DAYS = 35
    INCOME_AMOUNT_TOLERANCE = Decimal("20")
    ZERO = Decimal("0")
    ONE_HUNDRED = Decimal("100")
    TWO_DECIMALS = Decimal("0.01")

    @staticmethod
    def analyze_expense_category_growth(
        current_expenses: list[tuple[str, Decimal]],previous_expenses: list[tuple[str, Decimal]],
        current_total_expenses: Decimal,previous_total_expenses: Decimal,
    ) -> list[dict[str, Any]]:
        """
        G-01:
        Detecta categorías cuyo gasto aumentó al menos un 50 %,
        siempre que representaran al menos el 10 % del gastototal del período anterior.
        """
        if previous_total_expenses <= 0:
            return []
        current = dict(current_expenses)
        previous = dict(previous_expenses)
        recommendations = []
        for category, previous_amount in previous.items():
            current_amount = current.get(category)
            if current_amount is None or previous_amount <= 0:
                continue
            previous_share = (previous_amount / previous_total_expenses) * RecommendationFunctions.ONE_HUNDRED
            variation = (
                RecommendationFunctions.calculate_percentage_variation(current_amount,previous_amount,)
            )
            if (
                previous_share< RecommendationFunctions.EXPENSE_MIN_PREVIOUS_SHARE
                or variation< RecommendationFunctions.EXPENSE_GROWTH_THRESHOLD
            ):
                continue
            recommendations.append(
                RecommendationFunctions._build_recommendation(
                    rule_code="G-01",
                    area=RecommendationFunctions.Area.EXPENSES,
                    priority=RecommendationFunctions.Priority.HIGH,
                    title="Aumento del gasto por categoría",
                    message=(
                        f"El gasto en {category} aumentó {variation}% respecto al período anterior."
                    ),
                    data={
                        "category": category,
                        "current_amount": current_amount,
                        "previous_amount": previous_amount,
                        "variation_percentage": variation,
                        "previous_share_percentage": (
                            RecommendationFunctions._round(previous_share)
                        ),
                        "current_total_expenses": current_total_expenses,
                    },
                )
            )
        return recommendations

    @staticmethod
    def analyze_income_expense_imbalance(
        current_income: Decimal,current_expenses: Decimal,previous_income: Decimal,
    previous_expenses: Decimal,
    ) -> list[dict[str, Any]]:
        """
        G-02:
        Detecta cuando los gastos superan al menos un 20 % a
        los ingresos y la diferencia es relevante frente al
        volumen del período anterior.
        """
        if current_income <= 0:
            return []
        previous_volume = previous_income + previous_expenses
        if previous_volume <= 0:
            return []
        difference = current_expenses - current_income
        expense_income_ratio = current_expenses / current_income

        historical_share = (difference / previous_volume) * RecommendationFunctions.ONE_HUNDRED
        if (
            expense_income_ratio< RecommendationFunctions.EXPENSE_INCOME_RATIO_THRESHOLD
            or historical_share< RecommendationFunctions.IMBALANCE_MIN_HISTORICAL_SHARE
        ):
            return []
        return [
            RecommendationFunctions._build_recommendation(
                rule_code="G-02",
                area=RecommendationFunctions.Area.EXPENSES,
                priority=RecommendationFunctions.Priority.HIGH,
                title="Desequilibrio entre ingresos y gastos",
                message=(
                    "Los gastos superan significativamente "
                    "los ingresos del período."
                ),
                data={
                    "income": current_income,
                    "expenses": current_expenses,
                    "difference": difference,
                    "expense_income_ratio": (
                        RecommendationFunctions._round(
                            expense_income_ratio
                        )
                    ),
                    "historical_share_percentage": (
                        RecommendationFunctions._round(historical_share)
                    ),
                },
            )
        ]

    @staticmethod
    def analyze_sales_drop(current_sales: Decimal,previous_sales: Decimal,) -> list[dict[str, Any]]:
        """
        V-01:
        Detecta una caída de las ventas de al menos un 40 %.
        """
        if previous_sales <= 0:
            return []
        variation = (
            RecommendationFunctions.calculate_percentage_variation(
                current_sales,
                previous_sales,
            )
        )
        if variation is None or variation > (RecommendationFunctions.SALES_DROP_THRESHOLD):
            return []
        reduction = previous_sales - current_sales
        reduction_share = (reduction / previous_sales) * RecommendationFunctions.ONE_HUNDRED
        if (
            reduction_share< RecommendationFunctions.SALES_DROP_MIN_HISTORICAL_SHARE
        ):
            return []
        return [
            RecommendationFunctions._build_recommendation(
                rule_code="V-01",
                area=RecommendationFunctions.Area.SALES,
                priority=RecommendationFunctions.Priority.HIGH,
                title="Caída significativa de las ventas",
                message=(
                    f"Las ventas disminuyeron "
                    f"{abs(variation)}% respecto al período anterior."
                ),
                data={
                    "current_sales": current_sales,
                    "previous_sales": previous_sales,
                    "reduction_amount": reduction,
                    "variation_percentage": variation,
                },
            )
        ]

    @staticmethod
    def analyze_product_sales_growth(
        current_sales_by_product: list[tuple[str, Decimal]],previous_sales_by_product: list[tuple[str, Decimal]],
        previous_total_sales: Decimal,
    ) -> list[dict[str, Any]]:
        """
        V-02:
        Detecta productos con un crecimiento del importe vendido
        de al menos un 30 %, cuya participación anterior haya
        sido al menos el 5 % de las ventas totales anteriores.
        """
        if previous_total_sales <= 0:
            return []
        current = dict(current_sales_by_product)
        previous = dict(previous_sales_by_product)
        recommendations = []
        for product, previous_amount in previous.items():
            current_amount = current.get(product)
            if current_amount is None or previous_amount <= 0:
                continue
            previous_share = (previous_amount / previous_total_sales) * RecommendationFunctions.ONE_HUNDRED
            variation = (
                RecommendationFunctions.calculate_percentage_variation(
                    current_amount,previous_amount,
                )
            )
            if (
                previous_share< RecommendationFunctions.PRODUCT_MIN_PREVIOUS_SHARE
                or variation< RecommendationFunctions.PRODUCT_SALES_GROWTH_THRESHOLD
            ):
                continue
            recommendations.append(
                RecommendationFunctions._build_recommendation(
                    rule_code="V-02",
                    area=RecommendationFunctions.Area.SALES,
                    priority=RecommendationFunctions.Priority.OPPORTUNITY,
                    title="Producto con crecimiento en ventas",
                    message=(
                        f"El importe vendido de {product} aumentó "
                        f"{variation}% respecto al período anterior."
                    ),
                    data={
                        "product": product,
                        "current_amount": current_amount,
                        "previous_amount": previous_amount,
                        "variation_percentage": variation,
                        "previous_share_percentage": (
                            RecommendationFunctions._round(previous_share)
                        ),
                    },
                )
            )
        return recommendations

    @staticmethod
    def analyze_product_quantity_growth(
        current_quantities: list[tuple[str, Decimal]],previous_quantities: list[tuple[str, Decimal]],
        older_quantities: list[tuple[str, Decimal]],
    ) -> list[dict[str, Any]]:
        """
        V-04:
        Detecta productos que crecieron al menos un 30 % en
        dos comparaciones consecutivas entre tres períodos.
        """
        current = dict(current_quantities)
        previous = dict(previous_quantities)
        older = dict(older_quantities)
        recommendations = []
        for product, older_quantity in older.items():
            previous_quantity = previous.get(product)
            current_quantity = current.get(product)
            if (
                previous_quantity is None or current_quantity is None
                or older_quantity <= 0 or previous_quantity <= 0
            ):
                continue
            first_variation = (
                RecommendationFunctions.calculate_percentage_variation(
                    previous_quantity,older_quantity,
                )
            )
            second_variation = (
                RecommendationFunctions.calculate_percentage_variation(
                    current_quantity,previous_quantity,
                )
            )
            threshold = (RecommendationFunctions.PRODUCT_QUANTITY_GROWTH_THRESHOLD)
            if first_variation < threshold or second_variation < threshold:
                continue
            recommendations.append(
                RecommendationFunctions._build_recommendation(
                    rule_code="V-04",
                    area=RecommendationFunctions.Area.SALES,
                    priority=RecommendationFunctions.Priority.OPPORTUNITY,
                    title="Crecimiento sostenido de las ventas",
                    message=(
                        f"La cantidad vendida de {product} "
                        "creció en dos períodos consecutivos."
                    ),
                    data={
                        "product": product,
                        "older_quantity": older_quantity,
                        "previous_quantity": previous_quantity,
                        "current_quantity": current_quantity,
                        "first_variation_percentage": first_variation,
                        "second_variation_percentage": second_variation,
                    },
                )
            )
        return recommendations

    @staticmethod
    def analyze_sales_variability(daily_sales: list[tuple[date, Decimal]],) -> list[dict[str, Any]]:
        """
        V-06:
        Detecta una variabilidad diaria elevada. El servicio debe entregar todos los días del período,
        incluidos los días sin ventas con importe cero.
        """
        if not daily_sales:
            return []
        amounts = [float(amount) for _, amount in daily_sales]
        active_days = sum(amount > 0 for amount in amounts)
        if active_days< RecommendationFunctions.MIN_ACTIVE_SALES_DAYS:
            return []
        mean = sum(amounts) / len(amounts)
        if mean <= 0:
            return []
        variance = sum((amount - mean) ** 2 for amount in amounts) / len(amounts)
        std = sqrt(variance)
        coefficient_variation = (std / mean) * 100
        if (
            coefficient_variation<= float(RecommendationFunctions.SALES_CV_THRESHOLD)
        ):
            return []
        return [
            RecommendationFunctions._build_recommendation(
                rule_code="V-06",
                area=RecommendationFunctions.Area.SALES,
                priority=RecommendationFunctions.Priority.INFORMATIONAL,
                title="Alta variabilidad en las ventas",
                message=(
                    "Las ventas diarias presentan fluctuaciones "
                    "elevadas durante el período analizado."
                ),
                data={
                    "daily_mean": RecommendationFunctions._round(
                        Decimal(str(mean))
                    ),
                    "population_std": RecommendationFunctions._round(
                        Decimal(str(std))
                    ),
                    "coefficient_variation": (
                        RecommendationFunctions._round(
                            Decimal(str(coefficient_variation))
                        )
                    ),
                    "active_days": active_days,
                    "total_days": len(daily_sales),
                },
            )
        ]

    @staticmethod
    def analyze_income_periodicity(income_records: list[tuple[str, date, Decimal]],
    ) -> list[dict[str, Any]]:
        """
        I-04:
        Detecta posibles ingresos recurrentes por categoría.
        Requiere al menos tres registros, intervalos de 25 a 35
        días y montos dentro de un margen del 20 % respecto a la mediana de los importes.
        """
        grouped = defaultdict(list)
        for category, record_date, amount in income_records:
            grouped[category].append((record_date, amount))
        recommendations = []
        for category, records in grouped.items():
            records.sort(key=lambda record: record[0])
            if (len(records)< RecommendationFunctions.MIN_PERIODIC_INCOMES):
                continue
            dates = [record_date for record_date, _ in records]
            amounts = [amount for _, amount in records]
            intervals = [
                (dates[index] - dates[index - 1]).days
                for index in range(1, len(dates))
            ]
            if any(
                interval< RecommendationFunctions.MIN_INCOME_INTERVAL_DAYS
                or interval> RecommendationFunctions.MAX_INCOME_INTERVAL_DAYS
                for interval in intervals
            ):
                continue
            median_amount = Decimal(str(median(amounts)))
            if median_amount <= 0:
                continue
            tolerance = (
                RecommendationFunctions.INCOME_AMOUNT_TOLERANCE/ RecommendationFunctions.ONE_HUNDRED
            )
            amounts_are_similar = all(
                abs(amount - median_amount) / median_amount <= tolerance
                for amount in amounts
            )

            if not amounts_are_similar:
                continue

            average_interval = (Decimal(sum(intervals)) / Decimal(len(intervals)))
            recommendations.append(
                RecommendationFunctions._build_recommendation(
                    rule_code="I-04",
                    area=RecommendationFunctions.Area.INCOME,
                    priority=RecommendationFunctions.Priority.INFORMATIONAL,
                    title="Posible ingreso recurrente",
                    message=(
                        f"Se detectó un posible patrón de ingresos "
                        f"recurrentes en la categoría {category}."
                    ),
                    data={
                        "category": category,
                        "occurrences": len(records),
                        "first_date": dates[0],
                        "last_date": dates[-1],
                        "median_amount": median_amount,
                        "average_interval_days": (
                            RecommendationFunctions._round(average_interval)
                        ),
                    },
                )
            )
        return recommendations

    #*Métodos auxiliares
    @staticmethod
    def calculate_percentage_variation(current: Decimal,previous: Decimal,) -> Decimal | None:
        """
        Calcula la variación porcentual respecto al valor anterior.
        Devuelve None si el valor anterior no permite comparar.
        """
        if previous <= 0:
            return None
        variation = (
            (current - previous)/ previous* RecommendationFunctions.ONE_HUNDRED
        )
        return RecommendationFunctions._round(variation)

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        #*Redondea a dos decimales
        return value.quantize(
            RecommendationFunctions.TWO_DECIMALS,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _build_recommendation(
        rule_code: str,area: Area,priority: Priority,title: str,message: str,data: dict[str, Any],
    ) -> dict[str, Any]:
        #*Construye todas las recomendaciones con el mismo contrato.
        return {
            "rule_code": rule_code,
            "area": area.value,
            "priority": priority.value,
            "title": title,
            "message": message,
            "data": data,
        }
