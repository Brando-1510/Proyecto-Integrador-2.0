from app.models.movement import Movement
from app.models.sale import Sale
from decimal import Decimal
#*Importaciones relacionadas con las fechas
from datetime import timedelta
from app.utils.date_utils import DateUtils

class HomeDashboardService:
    def __init__(self,sale_repository,movement_repository):
        self.sale_repository=sale_repository
        self.movement_repository=movement_repository
    def dashboard_data(self,business_id):
        self.business_id=business_id
        start_date,end_date=DateUtils.last_30_days()
        #*Datos relacionados con los frame KPIs
        ventas=self.sale_repository.get_total_sales(self.business_id,start_date,end_date)
        gastos=self.movement_repository.get_expenses(self.business_id,start_date,end_date)
        ingresos=self.movement_repository.get_income(self.business_id,start_date,end_date)
        utilidad=ingresos-gastos
        #*Datos relacionados con la gráfica
        evolucion=self.get_sales_evolution_last_30_days(start_date,end_date)
        #*Datos para las tablas de movimientos y ventas recientes
        movimientos_recientes=self.movement_repository.get_recent_movements(self.business_id,start_date,end_date)
        ventas_recientes=self.sale_repository.get_recent_sales(self.business_id,start_date,end_date)
        #*Retornar datos
        return {
            "success":True,
            "fecha_inicio":start_date,
            "fecha_final": end_date,
            "ventas":ventas,
            "gastos":gastos,
            "ingresos":ingresos,
            "utilidad":utilidad,
            "evolucion_ventas":evolucion,
            "movimientos_recientes":movimientos_recientes,
            "ventas_recientes":ventas_recientes
        }
    def get_sales_evolution_last_30_days(self,start_date,end_date):
        results = self.sale_repository.get_sales_evolution_last_30_days(self.business_id,start_date,end_date)
        sales_by_date = {
            sale_date: total
            for sale_date, total in results
        }
        evolution = []
        current_date = start_date
        while current_date <= end_date:
            evolution.append(
                (
                    current_date,
                    sales_by_date.get(current_date, Decimal("0"))
                )
            )
            current_date += timedelta(days=1)
        return evolution