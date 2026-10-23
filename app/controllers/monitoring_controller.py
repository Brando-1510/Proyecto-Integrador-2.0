from app.services.monitoring_service import MonitoringService

class MonitoringController:
    def __init__(self, service: MonitoringService):
        self.service = service
    def send_data(self, business_id):
        try:
            resultado = self.service.send_data(business_id)
            return resultado
        except Exception:
            return {
                "success": False,
                "message": "No se pudo cargar la información"
            }
    def check_database_health(self):
        try:
            resultado = self.service.check_database_health()
            return resultado
        except Exception:
            return {
                "success": False,
                "message": "No se pudo comprobar el estado de la base de datos"
            }
    def optimize_tables(self):
        return self.service.optimize_tables()