from app.utils.format_utils import FormatUtils
class HomeDashboardController:
    def __init__(self,service):
        self.service=service
    def datos_dashboard(self,business_id):
        try:
            resultado=self.service.dashboard_data(business_id)
            fecha_inicio=resultado["fecha_inicio"]
            fecha_final=resultado["fecha_final"]
            rango_fecha=FormatUtils.date_range_short(fecha_inicio,fecha_final)
            return{
                "success":True,
                "rango_fecha":rango_fecha,
                "ventas":resultado["ventas"],
                "gastos":resultado["gastos"],
                "ingresos":resultado["ingresos"],
                "utilidad":resultado["utilidad"],
                "evolucion_ventas":resultado["evolucion_ventas"],
                "movimientos_recientes":resultado["movimientos_recientes"],
                "ventas_recientes":resultado["ventas_recientes"]
            }
        except Exception:
            import traceback
            traceback.print_exc()
            return{
                "success":False,
                "message":"Ocurrio un error al cargar los datos"
            }