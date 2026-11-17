from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import calendar
from app.database.connection import SessionLocal
from app.models.movement import MovementType
from app.models.user_business import Role
from app.repositories.business_repository import BusinessRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.repositories.user_repository import UserRepository
from app.services.report_analytics_service import ReportAnalyticsService
from app.services.report_insights_service import ReportInsightsService
from app.utils.date_utils import DateUtils

class ReportService:
    REPORT_TYPES = {"ventas", "ingresos", "gastos", "general"}
    ALLOWED_ROLES = {Role.ADMIN, Role.MANAGER, Role.FINANCIAL_ANALYST}
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def get_report_data(self, datos: dict) -> dict:
        #*Devuelve únicamente valores serializables, nunca entidades ORM
        report_type = datos.get("tipo_reporte")
        if report_type not in self.REPORT_TYPES:
            raise ValueError("Tipo de informe no válido.")
        business_id = datos.get("business_id")
        user_id = datos.get("user_id")
        if type(business_id) is not int or business_id <= 0:
            raise ValueError("El negocio seleccionado no es válido.")
        if type(user_id) is not int or user_id <= 0:
            raise ValueError("El usuario seleccionado no es válido.")
        start_date, end_date = self.obtener_rango_fechas(datos)
        duration = (end_date - start_date).days + 1
        prior_end = start_date - timedelta(days=1)
        prior_start = prior_end - timedelta(days=duration - 1)
        with self.session_factory() as session:
            business = BusinessRepository(session).get_by_id(business_id)
            user = UserRepository(session).get_by_id(user_id)
            if business is None or user is None:
                raise ValueError("El negocio o usuario seleccionado no existe.")
            role = UserBusinessRepository(session).get_role(user_id, business_id)
            if role not in self.ALLOWED_ROLES:
                raise PermissionError("No tienes autorización para generar informes de este negocio.")
            sale_repo = SaleRepository(session)
            movement_repo = MovementRepository(session)
            result: dict = {
                "metadata": {
                    "tipo_reporte": report_type,
                    "periodo": datos.get("periodo", "Personalizado"),
                    "fecha_inicio": start_date,
                    "fecha_fin": end_date,
                    "periodo_anterior_inicio": prior_start,
                    "periodo_anterior_fin": prior_end,
                    "negocio": business.business_name,
                    "creado_por": user.username,
                    "generado_el": datetime.now(),
                },
                "comparaciones": [],
            }
            # Se consulta una sola vez la evolución de movimientos, aun en un informe general.
            evolution_rows = (
                movement_repo.get_movement_evolution(business_id, start_date, end_date)
                if report_type in {"ingresos", "gastos", "general"} else []
            )
            if report_type in {"ventas", "general"}:
                result["ventas"] = self._get_sales_data(
                    sale_repo, business_id, start_date, end_date
                )
                previous = sale_repo.get_total_sales(business_id, prior_start, prior_end)
                result["comparaciones"].append(ReportAnalyticsService.compare(
                    "Ventas", result["ventas"]["total_vendido"], previous
                ))
            if report_type in {"ingresos", "general"}:
                result["ingresos"] = self._get_income_data(
                    movement_repo, business_id, start_date, end_date, evolution_rows
                )
                previous_income = movement_repo.get_income(business_id, prior_start, prior_end)
                result["comparaciones"].append(ReportAnalyticsService.compare(
                    "Ingresos", result["ingresos"]["total_ingresos"], previous_income
                ))
            else:
                previous_income = None
            if report_type in {"gastos", "general"}:
                result["gastos"] = self._get_expense_data(
                    movement_repo, business_id, start_date, end_date, evolution_rows
                )
                previous_expenses = movement_repo.get_expenses(business_id, prior_start, prior_end)
                result["comparaciones"].append(ReportAnalyticsService.compare(
                    "Gastos", result["gastos"]["total_gastos"], previous_expenses
                ))
            else:
                previous_expenses = None
            if report_type == "general":
                income = result["ingresos"]["total_ingresos"]
                expenses = result["gastos"]["total_gastos"]
                balance = income - expenses
                result["resumen"] = {
                    "ingresos": income,
                    "gastos": expenses,
                    "saldo_movimientos": balance,
                    "ventas": result["ventas"]["total_vendido"],
                    "ventas_realizadas": result["ventas"]["ventas_realizadas"],
                }
                result["comparaciones"].append(ReportAnalyticsService.compare(
                    "Saldo de movimientos", balance,
                    Decimal(str(previous_income or 0)) - Decimal(str(previous_expenses or 0))
                ))
            result["hallazgos"] = ReportInsightsService.generate(result)
            return result

    @staticmethod
    def obtener_rango_fechas(datos: dict) -> tuple[date, date]:
        periodo = datos.get("periodo")
        if periodo == "Personalizado":
            start_date = datos.get("rango_inicio")
            end_date = datos.get("rango_final")
            if start_date is None or end_date is None:
                raise ValueError("Debes seleccionar ambas fechas.")
            if type(start_date) is not date or type(end_date) is not date:
                raise ValueError("Las fechas seleccionadas no son válidas.")
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
            raise ValueError("La fecha inicial no puede ser posterior a la final.")
        if (end_date - start_date).days > 3650:
            raise ValueError("Selecciona un intervalo máximo de diez años.")
        return start_date, end_date

    @staticmethod
    def _get_sales_data(repository, business_id: int, start_date: date, end_date: date):
        total = Decimal(str(repository.get_total_sales(business_id, start_date, end_date) or 0))
        count = repository.get_sales_count(business_id, start_date, end_date) or 0
        average = (
            (total / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if count else Decimal("0.00")
        )
        category_rows = repository.get_sales_by_category(business_id, start_date, end_date)
        product_rows = repository.get_sales_by_product(business_id, start_date, end_date, limit=10)
        daily_rows = repository.get_sales_evolution_last_30_days(business_id, start_date, end_date)
        return {
            "total_vendido": total,
            "ticket_promedio": average,
            "ventas_realizadas": count,
            "evolucion": ReportService._prepare_evolution(daily_rows, start_date, end_date),
            "ventas_por_categoria": [
                {"nombre": name or "Sin categoría", "total": Decimal(str(amount or 0))}
                for name, amount in category_rows
            ],
            "ventas_por_producto": [
                {"nombre": name or "Sin descripción", "total": Decimal(str(amount or 0))}
                for name, amount in product_rows
            ],
        }
    @staticmethod
    def _get_income_data(repository, business_id, start_date, end_date, evolution_rows):
        total = Decimal(str(repository.get_income(business_id, start_date, end_date) or 0))
        categories = ReportService._prepare_categories(
            repository.get_movements_by_category(
                business_id, start_date, end_date, MovementType.INCOME
            ), total
        )
        rows = [(day, amount) for day, mtype, amount in evolution_rows
                if mtype == MovementType.INCOME]
        return {
            "total_ingresos": total,
            "categoria_mayor_ingreso": categories[0]["nombre"] if categories else None,
            "evolucion": ReportService._prepare_evolution(rows, start_date, end_date),
            "ingresos_por_categoria": categories,
        }

    @staticmethod
    def _get_expense_data(repository, business_id, start_date, end_date, evolution_rows):
        total = Decimal(str(repository.get_expenses(business_id, start_date, end_date) or 0))
        categories = ReportService._prepare_categories(
            repository.get_movements_by_category(
                business_id, start_date, end_date, MovementType.EXPENSE
            ), total
        )
        rows = [(day, amount) for day, mtype, amount in evolution_rows
                if mtype == MovementType.EXPENSE]
        return {
            "total_gastos": total,
            "categoria_mayor_gasto": categories[0]["nombre"] if categories else None,
            "evolucion": ReportService._prepare_evolution(rows, start_date, end_date),
            "gastos_por_categoria": categories,
        }

    @staticmethod
    def _prepare_categories(rows, total: Decimal) -> list[dict]:
        result = []
        for name, amount in rows:
            amount = Decimal(str(amount or 0))
            percent = (
                (amount / total * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if total != 0 else Decimal("0")
            )
            result.append({
                "nombre": name.strip() if name and name.strip() else "Sin categoría",
                "total": amount,
                "porcentaje": percent,
            })
        return result

    @staticmethod
    def _prepare_evolution(rows, start_date: date, end_date: date) -> list[dict]:
        #*Solo crea series con datos reales; incluye ceros para días intermedios
        if not rows:
            return []
        days = (end_date - start_date).days + 1
        granularity = "daily" if days <= 60 else "weekly" if days <= 365 else "monthly"
        totals = {day: Decimal(str(amount or 0)) for day, amount in rows}
        buckets: dict = {}
        current = start_date
        while current <= end_date:
            if granularity == "daily":
                bucket_start = bucket_end = current
            elif granularity == "weekly":
                monday = current - timedelta(days=current.weekday())
                bucket_start = max(monday, start_date)
                bucket_end = min(monday + timedelta(days=6), end_date)
            else:
                month_end = current.replace(day=calendar.monthrange(current.year, current.month)[1])
                bucket_start = max(current.replace(day=1), start_date)
                bucket_end = min(month_end, end_date)
            if bucket_start not in buckets:
                buckets[bucket_start] = {
                    "fecha_inicio": bucket_start,
                    "fecha_fin": bucket_end,
                    "total": Decimal("0.00"),
                }
            buckets[bucket_start]["total"] += totals.get(current, Decimal("0.00"))
            current += timedelta(days=1)
        return list(buckets.values())
