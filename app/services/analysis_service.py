#Análisis financiero determinista, independiente de Recomendaciones y HomeDashboard
from datetime import date, timedelta
from decimal import Decimal
from app.database.connection import SessionLocal
from app.models.user_business import Role
from app.repositories.user_business_repository import UserBusinessRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.utils.date_utils import DateUtils
from app.utils.analysis.comparison_functions import ComparisonFunctions
from app.utils.analysis.finding_functions import FindingFunctions
from app.utils.analysis.statistical_functions import StatisticalFunctions


class AnalysisService:
    ALLOWED_ROLES = {Role.ADMIN, Role.MANAGER, Role.FINANCIAL_ANALYST}

    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def analyze_period(self, datos: dict) -> dict:
        business_id = datos.get("business_id")
        user_id = datos.get("user_id")
        if business_id is None or user_id is None:
            raise ValueError("Debes seleccionar un negocio y un usuario válido.")
        start_date, end_date = self.obtener_rango_fechas(datos)
        days = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days - 1)
        with self.session_factory() as session:
            actual_role = UserBusinessRepository(session).get_role(user_id, business_id)
            self.verify_role(actual_role)
            repo = AnalysisRepository(session)
            current = self._analyze_current(repo, business_id, start_date, end_date)
            previous_income, previous_expenses = repo.total_income_expenses(
                business_id, previous_start, previous_end
            )

        prev_income = Decimal(str(previous_income))
        prev_expenses = Decimal(str(previous_expenses))
        current_stats = current["statistics"]
        comparisons = {
            "income": ComparisonFunctions.analyze_income_variation(
                current_stats["income"], prev_income
            ),
            "expenses": ComparisonFunctions.analyze_expense_variation(
                current_stats["expenses"], prev_expenses
            ),
            "balance": ComparisonFunctions.analyze_balance_variation(
                current_stats["balance"], prev_income - prev_expenses
            ),
        }
        findings = []
        # No generar hallazgos vacíos cuando ambos períodos carecen de actividad.
        if current_stats["income"] != 0 or prev_income != 0:
            findings.append(FindingFunctions.build_income_finding(comparisons["income"]))
        if current_stats["expenses"] != 0 or prev_expenses != 0:
            findings.append(FindingFunctions.build_expense_finding(comparisons["expenses"]))
        categories = current["categories"]
        for analyzer, builder, key in (
            (FindingFunctions.analyze_expense_category, FindingFunctions.build_expense_category_finding, "expenses"),
            (FindingFunctions.analyze_income_category, FindingFunctions.build_income_category_finding, "income"),
            (FindingFunctions.analyze_sales_category, FindingFunctions.build_sales_category_finding, "sales"),
        ):
            finding = builder(analyzer(categories[key]))
            if finding is not None:
                findings.append(finding)
        sales_stats = current["sales_statistics"]
        if sales_stats["total_sales"] > 0:
            findings.append(FindingFunctions.build_sales_variability_finding(sales_stats["variability"]))
        return {
            "success": True,
            "period": current["period"],
            "previous_period": {"start_date": previous_start, "end_date": previous_end},
            "statistics": current_stats,
            "charts": current["charts"],
            "categories": categories,
            "sales_statistics": sales_stats,
            "comparisons": comparisons,
            "findings": findings,
            "has_data": current["has_data"],
        }

    @staticmethod
    def _analyze_current(repo, business_id: int, start_date: date, end_date: date) -> dict:
        income, expenses = repo.total_income_expenses(business_id, start_date, end_date)
        income, expenses = Decimal(str(income)), Decimal(str(expenses))
        performance = repo.get_financial_performance(business_id, start_date, end_date)
        expense_categories = repo.get_expenses_category(business_id, start_date, end_date)
        income_categories = repo.get_income_category(business_id, start_date, end_date)
        sales_result = repo.get_sales_indicators(business_id, start_date, end_date)
        sales_categories = repo.get_sales_category(business_id, start_date, end_date)

        count = int(sales_result.TotalVentas)
        sales_sum = Decimal(str(sales_result.SumaTotalVentas))
        sales_stats = StatisticalFunctions.from_aggregates(
            count, sales_sum, sales_result.SumaCuadrados
        )
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "statistics": {"income": income, "expenses": expenses, "balance": income - expenses},
            "charts": {"financial_performance": [
                {"interval": r[0], "income": r[1], "expenses": r[2]} for r in performance
            ]},
            "categories": {
                "expenses": [{"category": r[0], "amount": r[1]} for r in expense_categories],
                "income": [{"category": r[0], "amount": r[1]} for r in income_categories],
                "sales": [{"category": r[0], "amount": r[1]} for r in sales_categories],
            },
            "sales_statistics": {
                "total_sales": count, "total_amount": sales_sum,
                "average_ticket": sales_stats["mean"], "variability": sales_stats,
            },
            "has_data": bool(performance or expense_categories or income_categories or count),
        }

    @staticmethod
    def verify_role(rol) -> bool:
        if rol not in AnalysisService.ALLOWED_ROLES:
            raise PermissionError("No tienes permisos para analizar los datos de este negocio.")
        return True

    @staticmethod
    def obtener_rango_fechas(datos: dict) -> tuple[date, date]:
        periodo = datos.get("periodo")
        if periodo == "Personalizado":
            start_date, end_date = datos.get("rango_inicio"), datos.get("rango_final")
            if start_date is None or end_date is None:
                raise ValueError("Debes seleccionar ambas fechas.")
        elif periodo == "Esta Semana":
            start_date, end_date = DateUtils.this_week()
        elif periodo == "Este Mes":
            start_date, end_date = DateUtils.this_month()
        elif periodo == "Los Últimos 3 Meses":
            start_date, end_date = DateUtils.last_3_months()
        elif periodo in ("Último Año", "Últimos 12 Meses"):
            start_date, end_date = DateUtils.last_year()
        else:
            raise ValueError(f"Período no válido: {periodo}")
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise ValueError("Las fechas deben ser fechas válidas.")
        if start_date > end_date:
            raise ValueError("La fecha inicial no puede ser posterior a la final.")
        return start_date, end_date
