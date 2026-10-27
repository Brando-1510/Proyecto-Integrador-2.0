from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import calendar
from app.database.connection import SessionLocal
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.models.movement import MovementType
from app.utils.date_utils import DateUtils

class ReportService:
    REPORT_TYPES = {"ventas", "ingresos", "gastos", "general"}
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    # Entrada principal
    def get_report_data(self, datos: dict) -> dict:
        report_type = datos.get("tipo_reporte")
        if report_type not in self.REPORT_TYPES:
            raise ValueError("Tipo de informe no válido.")
        business_id = datos.get("business_id")
        user_id = datos.get("user_id")
        if not isinstance(business_id, int) or business_id <= 0:
            raise ValueError("El negocio seleccionado no es válido.")
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("El usuario seleccionado no es válido.")
        start_date, end_date = self.obtener_rango_fechas(datos)
        with self.session_factory() as session:
            business_repo = BusinessRepository(session)
            user_repo = UserRepository(session)
            sale_repo = SaleRepository(session)
            movement_repo = MovementRepository(session)
            business = business_repo.get_by_id(business_id)
            user_business_repo = UserBusinessRepository(session)
            user = user_repo.get_by_id(user_id)
            if business is None:
                raise ValueError("El negocio seleccionado no existe.")
            if user is None:
                raise ValueError("El usuario seleccionado no existe.")
            if not user_business_repo.exists_relationship(user_id,business_id,):
                raise ValueError("No tienes acceso al negocio seleccionado.")
            result = {
                "metadata": {
                    "tipo_reporte": report_type,
                    "periodo": datos["periodo"],
                    "fecha_inicio": start_date,
                    "fecha_fin": end_date,
                    "negocio": business.business_name,
                    "creado_por": user.username,
                }
            }
            if report_type in {"ventas", "general"}:
                result["ventas"] = self._get_sales_data(
                    sale_repo,
                    business_id,
                    start_date,
                    end_date,
                )
            if report_type in {"ingresos", "general"}:
                result["ingresos"] = self._get_income_data(
                    movement_repo,
                    business_id,
                    start_date,
                    end_date,
                )
            if report_type in {"gastos", "general"}:
                result["gastos"] = self._get_expense_data(
                    movement_repo,
                    business_id,
                    start_date,
                    end_date,
                )
            return result

    # Resolución del período
    def obtener_rango_fechas(self, datos: dict) -> tuple[date, date]:
        periodo = datos.get("periodo")
        if periodo == "Personalizado":
            start_date = datos.get("rango_inicio")
            end_date = datos.get("rango_final")
            if start_date is None or end_date is None:
                raise ValueError("Debes seleccionar ambas fechas.")
            if not isinstance(start_date, date) or not isinstance(end_date, date):
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
        return start_date, end_date

    #*Ventas
    def _get_sales_data(
        self,repository,business_id: int,start_date: date,end_date: date,
    ) -> dict:
        total = Decimal(
            str(repository.get_total_sales(business_id, start_date, end_date))
        )
        count = repository.get_sales_count(business_id, start_date, end_date)
        count = count or 0
        average = (
            (total / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if count > 0
            else Decimal("0.00")
        )
        category_rows = repository.get_sales_by_category(business_id, start_date, end_date)
        product_rows = repository.get_sales_by_product(business_id, start_date, end_date)
        category_data = [
            {
                "nombre": name,
                "total": Decimal(str(amount or 0)),
            }
            for name, amount in category_rows
        ]
        product_data = [
            {
                "nombre": name,
                "total": Decimal(str(amount or 0)),
            }
            for name, amount in product_rows[:10]
        ]
        daily_rows = repository.get_sales_evolution_last_30_days(
            business_id, start_date, end_date
        )
        return {
            "total_vendido": total,
            "ticket_promedio": average,
            "ventas_realizadas": count,
            "evolucion": self._prepare_evolution(
                daily_rows, start_date, end_date
            ),
            "ventas_por_categoria": category_data,
            "ventas_por_producto": product_data,
        }
    # Ingresos
    def _get_income_data(
        self,repository,business_id: int,start_date: date,end_date: date,
    ) -> dict:
        total = Decimal(str(repository.get_income(business_id, start_date, end_date)))
        category_rows = repository.get_movements_by_category(
            business_id,start_date,end_date,MovementType.INCOME,
        )
        categories = self._prepare_categories(category_rows, total)
        evolution_rows = repository.get_movement_evolution(business_id, start_date, end_date)
        daily_rows = [
            (day, amount)
            for day, movement_type, amount in evolution_rows
            if movement_type == MovementType.INCOME
        ]
        return {
            "total_ingresos": total,
            "categoria_mayor_ingreso": (
                categories[0]["nombre"] if categories else None
            ),
            "evolucion": self._prepare_evolution(
                daily_rows, start_date, end_date
            ),
            "ingresos_por_categoria": categories,
        }
    # Gastos
    def _get_expense_data(
        self,repository,business_id: int,start_date: date,end_date: date,
    ) -> dict:
        total = Decimal(
            str(repository.get_expenses(business_id, start_date, end_date))
        )
        category_rows = repository.get_movements_by_category(
            business_id,start_date,end_date,MovementType.EXPENSE,
        )
        categories = self._prepare_categories(category_rows, total)
        evolution_rows = repository.get_movement_evolution(business_id, start_date, end_date)
        daily_rows = [
            (day, amount)
            for day, movement_type, amount in evolution_rows
            if movement_type == MovementType.EXPENSE
        ]
        return {
            "total_gastos": total,
            "categoria_mayor_gasto": (
                categories[0]["nombre"] if categories else None
            ),
            "evolucion": self._prepare_evolution(
                daily_rows, start_date, end_date
            ),
            "gastos_por_categoria": categories,
        }
    #*Categorías
    @staticmethod
    def _prepare_categories(rows, total: Decimal) -> list[dict]:
        result = []
        for name, amount in rows:
            amount = Decimal(str(amount or 0))
            percentage = (
                round(float(amount / total * 100), 2)
                if total > 0
                else 0.0
            )
            result.append({
                "nombre": name.strip() if name else "Sin categoría",
                "total": amount,
                "porcentaje": percentage,
            })
        return result

    # Series temporales
    @staticmethod
    def _prepare_evolution(rows,start_date: date,end_date: date,) -> list[dict]:
        days = (end_date - start_date).days + 1
        if days <= 60:
            granularity = "daily"
        elif days <= 365:
            granularity = "weekly"
        else:
            granularity = "monthly"
        daily_totals = {
            day: Decimal(str(amount or 0))
            for day, amount in rows
        }
        buckets = {}
        current = start_date
        while current <= end_date:
            if granularity == "daily":
                bucket_start = current
                bucket_end = current
            elif granularity == "weekly":
                monday = current - timedelta(days=current.weekday())
                sunday = monday + timedelta(days=6)
                bucket_start = max(monday, start_date)
                bucket_end = min(sunday, end_date)
            else:
                last_day = calendar.monthrange(current.year, current.month)[1]
                month_start = current.replace(day=1)
                month_end = current.replace(day=last_day)
                bucket_start = max(month_start, start_date)
                bucket_end = min(month_end, end_date)
            key = bucket_start
            if key not in buckets:
                buckets[key] = {
                    "fecha_inicio": bucket_start,
                    "fecha_fin": bucket_end,
                    "total": Decimal("0.00"),
                }
            buckets[key]["total"] += daily_totals.get(current, Decimal("0.00"))
            current += timedelta(days=1)
        return list(buckets.values())