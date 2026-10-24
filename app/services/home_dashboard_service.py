from decimal import Decimal
from datetime import timedelta
from app.database.connection import SessionLocal
from app.utils.date_utils import DateUtils
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository

class HomeDashboardService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def dashboard_data(self, business_id):
        start_date, end_date = DateUtils.last_30_days()
        with self.session_factory() as session:
            sale_repository = SaleRepository(session)
            movement_repository = MovementRepository(session)
            #*Datos de las tarjetas KPI.
            ventas = sale_repository.get_total_sales(business_id,start_date,end_date)
            gastos = movement_repository.get_expenses(business_id,start_date,end_date)
            ingresos = movement_repository.get_income(business_id,start_date,end_date)
            utilidad = ingresos - gastos
            #*Evolución de las ventas.
            evolucion = self.get_sales_evolution_last_30_days(
                sale_repository,
                business_id,
                start_date,
                end_date
            )
            #*Datos para las tablas recientes.
            movimientos_recientes = movement_repository.get_movements(business_id,start_date,end_date)
            ventas_recientes = sale_repository.get_sales(business_id,start_date,end_date)
            #*Preparar los datos antes de cerrar la sesión.
            movimientos_recientes = list(movimientos_recientes)
            ventas_recientes = list(ventas_recientes)
            return {
                "success": True,
                "fecha_inicio": start_date,
                "fecha_final": end_date,
                "ventas": ventas,
                "gastos": gastos,
                "ingresos": ingresos,
                "utilidad": utilidad,
                "evolucion_ventas": evolucion,
                "movimientos_recientes": movimientos_recientes,
                "ventas_recientes": ventas_recientes
            }

    def get_sales_evolution_last_30_days(self,sale_repository,business_id,start_date,end_date):
        results = sale_repository.get_sales_evolution_last_30_days(business_id,start_date,end_date)
        sales_by_date = {
            sale_date: total
            for sale_date, total in results
        }
        evolution = []
        current_date = start_date
        while current_date <= end_date:
            evolution.append(
                (current_date,sales_by_date.get(current_date, Decimal("0")))
            )
            current_date += timedelta(days=1)
        return evolution
