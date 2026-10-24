from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from app.database.connection import SessionLocal
from app.repositories.recommendation_repository import RecommendationRepository
from app.utils.recommendation_functions import RecommendationFunctions
from app.utils.date_utils import DateUtils

class RecommendationService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    #*Obtener el período seleccionado.
    @staticmethod
    def _get_current_period(periodo: str) -> tuple[date, date]:
        if periodo == "Los Últimos 15 Días":
            return DateUtils.last_15_days()
        elif periodo == "Este Mes":
            return DateUtils.this_month()
        elif periodo == "Los Últimos 3 Meses":
            return DateUtils.last_3_months()
        elif periodo == "Último Año":
            return DateUtils.last_year()
        raise ValueError(f"Período no válido: {periodo}")

    #*Calcular períodos equivalentes.
    @staticmethod
    def _get_comparison_periods(start_date: date,end_date: date,) -> tuple[date, date, date, date]:
        duration = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=duration - 1)
        older_end = previous_start - timedelta(days=1)
        older_start = older_end - timedelta(days=duration - 1)
        return (
            previous_start,
            previous_end,
            older_start,
            older_end,
        )
    #*Completar los días sin ventas.
    @staticmethod
    def _complete_daily_sales(daily_sales: list[tuple[date, Decimal]],start_date: date,end_date: date,
    ) -> list[tuple[date, Decimal]]:
        sales_by_date = {
            day: Decimal(str(amount or 0))
            for day, amount in daily_sales
        }
        complete_sales = []
        current_date = start_date
        while current_date <= end_date:
            complete_sales.append(
                (
                    current_date,
                    sales_by_date.get(
                        current_date,
                        Decimal("0"),
                    ),
                )
            )
            current_date += timedelta(days=1)
        return complete_sales

    # Generar todas las recomendaciones.
    def generar_recomendaciones(self,datos: dict[str, Any],) -> dict[str, Any]:
        periodo = datos.get("periodo")
        business_id = datos.get("business_id")
        rol = datos.get("rol")
        if not periodo:
            raise ValueError("Debes seleccionar un período.")
        if (
            not isinstance(business_id, int)
            or isinstance(business_id, bool)
            or business_id <= 0
        ):
            raise ValueError("El negocio seleccionado no es válido.")
        if not rol:
            raise ValueError("No se ha especificado el rol del usuario.")
        # Calcular los tres períodos.
        start_date, end_date = self._get_current_period(periodo)
        (previous_start,previous_end,older_start,older_end,) = self._get_comparison_periods(start_date, end_date)
        # Abrir una sesión nueva para esta consulta.
        with self.session_factory() as session:
            repository = RecommendationRepository(session)
            recomendaciones = self._analizar_recomendaciones(
                repository=repository,
                business_id=business_id,
                start_date=start_date,
                end_date=end_date,
                previous_start=previous_start,
                previous_end=previous_end,
                older_start=older_start,
                older_end=older_end,
            )
        return {
            "success": True,
            "period": {
                "name": periodo,
                "start_date": start_date,
                "end_date": end_date,
                "previous_start_date": previous_start,
                "previous_end_date": previous_end,
            },
            "business_id": business_id,
            "rol": rol,
            "recommendations": recomendaciones,
            "total": len(recomendaciones),
        }
    def _analizar_recomendaciones(
        self,repository: RecommendationRepository,business_id: int,start_date: date,
        end_date: date,previous_start: date,previous_end: date,older_start: date,older_end: date,
    ) -> list[dict[str, Any]]:
        recomendaciones = []
        #*G-01: Aumento del gasto por categoría.
        current_expenses_by_category = (
            repository.get_expenses_by_category(business_id, start_date, end_date)
        )
        previous_expenses_by_category = (
            repository.get_expenses_by_category(business_id, previous_start, previous_end)
        )
        current_income, current_expenses = (
            repository.get_income_expense_totals(business_id, start_date, end_date)
        )
        previous_income, previous_expenses = (
            repository.get_income_expense_totals(business_id, previous_start, previous_end)
        )
        recomendaciones.extend(
            RecommendationFunctions.analyze_expense_category_growth(
                current_expenses_by_category,
                previous_expenses_by_category,
                current_expenses,
                previous_expenses,
            )
        )
        #*G-02: Desequilibrio entre ingresos y gastos.
        recomendaciones.extend(
            RecommendationFunctions.analyze_income_expense_imbalance(
                current_income,
                current_expenses,
                previous_income,
                previous_expenses,
            )
        )
        #*V-01: Caída significativa de las ventas.
        current_sales = repository.get_sales_total(business_id, start_date, end_date)
        previous_sales = repository.get_sales_total(business_id, previous_start, previous_end)
        recomendaciones.extend(
            RecommendationFunctions.analyze_sales_drop(current_sales,previous_sales,)
        )
        #*V-02: Crecimiento del importe vendido por producto.
        current_sales_by_product = repository.get_sales_by_product(business_id, start_date, end_date)
        previous_sales_by_product = repository.get_sales_by_product(business_id, previous_start, previous_end)
        recomendaciones.extend(
            RecommendationFunctions.analyze_product_sales_growth(
                current_sales_by_product,
                previous_sales_by_product,
                previous_sales,
            )
        )

        #*V-04: Crecimiento sostenido de cantidades vendidas.
        previous_quantities = repository.get_quantity_by_product(business_id, previous_start, previous_end)
        current_quantities = repository.get_quantity_by_product(business_id, start_date, end_date)
        older_quantities = repository.get_quantity_by_product(business_id, older_start, older_end)
        recomendaciones.extend(
            RecommendationFunctions.analyze_product_quantity_growth(
                current_quantities,
                previous_quantities,
                older_quantities,
            )
        )
        #*V-06: Variabilidad diaria de las ventas.
        daily_sales = repository.get_daily_sales(business_id, start_date, end_date)
        daily_sales = self._complete_daily_sales(daily_sales, start_date, end_date)
        recomendaciones.extend(RecommendationFunctions.analyze_sales_variability(daily_sales))
        # I-04: Posibles ingresos recurrentes.
        income_history_start = end_date - timedelta(days=89)
        income_records = repository.get_income_records_by_category(
            business_id,income_history_start,end_date,
        )
        recomendaciones.extend(RecommendationFunctions.analyze_income_periodicity(income_records))
        return recomendaciones
