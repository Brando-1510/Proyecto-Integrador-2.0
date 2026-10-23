from app.repositories.monitoring_repository import MonitoringRepository
from app.models.user_business import UserBusiness
from app.models.business import Business
from app.models.sale import Sale
from app.models.movement import Movement
from app.models.imports import Import

class MonitoringService:
    def __init__(self, repository: MonitoringRepository):
        self.repository = repository
        self.tables_to_check = {
            "Empleados": UserBusiness,
            "Negocios": Business,
            "Ventas": Sale,
            "Movimientos": Movement,
            "Importaciones": Import,
        }

    def send_data(self, business_id: int):
        empleados = self.repository.count_employees(business_id)
        ventas = self.repository.count_sales(business_id)
        movimientos = self.repository.count_movements(business_id)
        importaciones = self.repository.count_imports(business_id)
        return {
            "success": True,
            "empleados": empleados,
            "ventas": ventas,
            "movimientos": movimientos,
            "importaciones": importaciones
        }

    def check_database_health(self):
        results = []
        for name, model in self.tables_to_check.items():
            result = self.repository.check_table(model)
            results.append({
                "name": name,
                **result
            })
        return {
            "success": True,
            "tables": results
        }
    def optimize_tables(self):
        if self.repository.optimize_tables():
            return {
                "success":True,
                "message":"Se realizo la optimización de las tablas exitosamente"
            }
        return{
            "success":False,
            "message":"Ocurrio un error al optimizar la tabla"
        }
