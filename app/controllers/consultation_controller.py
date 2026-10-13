from app.utils.format_utils import FormatUtils

class ConsultationController:
    def __init__(self,service):
        self.service=service
    def mostrar_ventas(self,datos):
        try:
            resultado=self.service.get_sales(datos)
            fecha_inicio=resultado["fecha_inicio"]
            fecha_final=resultado["fecha_final"]
            rango_fecha=FormatUtils.date_range_long(fecha_inicio,fecha_final)
            return{
                "success":True,
                "tipo":"Ventas",
                "rango_fecha":rango_fecha,
                "ventas": resultado["ventas"]
            }
        except Exception:
            import traceback
            traceback.print_exc()
            return{
                "success":False,
                "message":"Ocurrio un error al cargar los datos"
            }
    def mostrar_movimientos(self,datos):
        try:
            resultado=self.service.get_movements(datos)
            fecha_inicio=resultado["fecha_inicio"]
            fecha_final=resultado["fecha_final"]
            rango_fecha=FormatUtils.date_range_long(fecha_inicio,fecha_final)
            return{
                "success":True,
                "tipo": "Movimientos",
                "rango_fecha":rango_fecha,
                "movimientos": resultado["movimientos"]
            }
        except Exception:
            import traceback
            traceback.print_exc()
            return{
                "success":False,
                "message":"Ocurrio un error al cargar los datos"
            }