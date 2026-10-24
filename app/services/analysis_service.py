
from datetime import date, timedelta
from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.user_business import Role
from app.repositories.analysis_repository import AnalysisRepository
from app.utils.date_utils import DateUtils
from app.utils.analysis.comparison_functions import ComparisonFunctions
from app.utils.analysis.finding_functions import FindingFunctions
from app.utils.analysis.statistical_functions import StatisticalFunctions


class AnalysisService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def analyze_period(self, datos: dict) -> dict:
        # Validar permisos.
        self.verify_role(datos["rol"])

        business_id = datos.get("business_id")
        if business_id is None:
            raise ValueError("Debes seleccionar un negocio.")

        start_date, end_date = self.obtener_rango_fechas(datos)

        # Analizar el período seleccionado.
        current = self._analyze_range(
            business_id,
            start_date,
            end_date
        )

        # Calcular el período anterior equivalente.
        duration = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=duration - 1)

        previous = self._analyze_range(
            business_id,
            previous_start,
            previous_end
        )

        current_stats = current["statistics"]
        previous_stats = previous["statistics"]

        # Comparaciones entre períodos.
        income_comparison = (
            ComparisonFunctions.analyze_income_variation(
                current_stats["income"],
                previous_stats["income"]
            )
        )

        expense_comparison = (
            ComparisonFunctions.analyze_expense_variation(
                current_stats["expenses"],
                previous_stats["expenses"]
            )
        )

        balance_comparison = (
            ComparisonFunctions.analyze_balance_variation(
                current_stats["balance"],
                previous_stats["balance"]
            )
        )

        comparisons = {
            "income": income_comparison,
            "expenses": expense_comparison,
            "balance": balance_comparison
        }

        # Generar hallazgos sobre las variaciones.
        findings = [
            FindingFunctions.build_income_finding(
                income_comparison
            ),
            FindingFunctions.build_expense_finding(
                expense_comparison
            )
        ]

        # Analizar las categorías.
        categories = current["categories"]

        expense_category_analysis = (
            FindingFunctions.analyze_expense_category(
                categories["expenses"]
            )
        )

        income_category_analysis = (
            FindingFunctions.analyze_income_category(
                categories["income"]
            )
        )

        sales_category_analysis = (
            FindingFunctions.analyze_sales_category(
                categories["sales"]
            )
        )

        # Construir hallazgos de categorías.
        category_findings = [
            FindingFunctions.build_expense_category_finding(
                expense_category_analysis
            ),
            FindingFunctions.build_income_category_finding(
                income_category_analysis
            ),
            FindingFunctions.build_sales_category_finding(
                sales_category_analysis
            )
        ]

        findings.extend(
            finding
            for finding in category_findings
            if finding is not None
        )

        # Hallazgo de variabilidad de ventas.
        sales_stats = current["sales_statistics"]

        if sales_stats["total_sales"] > 0:
            findings.append(
                FindingFunctions.build_sales_variability_finding(
                    sales_stats["variability"]
                )
            )

        # Mantener el contrato de retorno existente.
        return {
            "success": True,
            "period": current["period"],
            "statistics": current_stats,
            "charts": current["charts"],
            "categories": current["categories"],
            "sales_statistics": sales_stats,
            "comparisons": comparisons,
            "findings": findings,
            "previous_period": previous["period"]
        }

    def _analyze_range(
        self,
        business_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        # Cada período utiliza una sesión propia.
        # Todas sus consultas comparten la misma sesión.
        with self.session_factory() as session:
            analysis_repository = AnalysisRepository(session)

            # Indicadores financieros.
            income, expenses = (
                analysis_repository.total_income_expenses(
                    business_id,
                    start_date,
                    end_date
                )
            )

            income = Decimal(str(income))
            expenses = Decimal(str(expenses))
            balance = income - expenses

            # Datos para la gráfica de ingresos y gastos.
            performance = (
                analysis_repository.get_financial_performance(
                    business_id,
                    start_date,
                    end_date
                )
            )

            # Gastos e ingresos por categoría.
            expense_categories = (
                analysis_repository.get_expenses_category(
                    business_id,
                    start_date,
                    end_date
                )
            )

            income_categories = (
                analysis_repository.get_income_category(
                    business_id,
                    start_date,
                    end_date
                )
            )

            # Indicadores y categorías de ventas.
            sales_result = (
                analysis_repository.get_sales_indicators(
                    business_id,
                    start_date,
                    end_date
                )
            )

            sales_categories = (
                analysis_repository.get_sales_category(
                    business_id,
                    start_date,
                    end_date
                )
            )

            individual_sales = (
                analysis_repository.individual_sales_amount(
                    business_id,
                    start_date,
                    end_date
                )
            )

            # Extraer importes individuales.
            sales_amounts = [
                row[0]
                for row in individual_sales
            ]

            # Funciones estadísticas.
            mean = StatisticalFunctions.calculate_mean(
                sales_amounts
            )

            std = StatisticalFunctions.calculate_population_std(
                sales_amounts
            )

            cv = StatisticalFunctions.calculate_coefficient_variation(
                mean,
                std
            )

            classification = (
                StatisticalFunctions.classify_coefficient_variation(cv)
            )

            variability = {
                "mean": mean,
                "std": std,
                "coefficient_variation": cv,
                "classification": classification
            }

            total_sales = sales_result.TotalVentas
            sales_amount = Decimal(
                str(sales_result.SumaTotalVentas)
            )

            # Construir el resultado antes de cerrar la sesión.
            # Se conservan las claves y los tipos de salida existentes.
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "statistics": {
                    "income": income,
                    "expenses": expenses,
                    "balance": balance
                },
                "charts": {
                    "financial_performance": [
                        {
                            "interval": row[0],
                            "income": row[1],
                            "expenses": row[2]
                        }
                        for row in performance
                    ]
                },
                "categories": {
                    "expenses": [
                        {
                            "category": row[0],
                            "amount": row[1]
                        }
                        for row in expense_categories
                    ],
                    "income": [
                        {
                            "category": row[0],
                            "amount": row[1]
                        }
                        for row in income_categories
                    ],
                    "sales": [
                        {
                            "category": row[0],
                            "amount": row[1]
                        }
                        for row in sales_categories
                    ]
                },
                "sales_statistics": {
                    "total_sales": total_sales,
                    "total_amount": sales_amount,
                    "average_ticket": mean,
                    "variability": variability
                }
            }

    @staticmethod
    def verify_role(rol) -> bool:
        if rol == Role.EMPLOYEE:
            raise PermissionError(
                "El usuario no tiene el rol permitido "
                "para acceder a esta sección."
            )

        return True

    @staticmethod
    def obtener_rango_fechas(
        datos: dict
    ) -> tuple[date, date]:
        periodo = datos["periodo"]

        if periodo == "Personalizado":
            start_date = datos.get("rango_inicio")
            end_date = datos.get("rango_final")

            if start_date is None or end_date is None:
                raise ValueError("Debes seleccionar ambas fechas.")

        elif periodo == "Esta Semana":
            start_date, end_date = DateUtils.this_week()

        elif periodo == "Este Mes":
            start_date, end_date = DateUtils.this_month()

        elif periodo == "Los Últimos 3 Meses":
            start_date, end_date = DateUtils.last_3_months()

        elif periodo == "Último Año":
            start_date, end_date = DateUtils.last_year()

        else:
            raise ValueError(f"Período no válido: {periodo}")

        if start_date > end_date:
            raise ValueError(
                "La fecha inicial no puede ser posterior a la final."
            )

        return start_date, end_date
