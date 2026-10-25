from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import SessionLocal
from app.repositories.monitoring_repository import MonitoringRepository
from app.models.user_business import UserBusiness
from app.models.business import Business
from app.models.sale import Sale
from app.models.movement import Movement
from app.models.imports import Import

class MonitoringService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.tables_to_check = {
            "Empleados": UserBusiness,
            "Negocios": Business,
            "Ventas": Sale,
            "Movimientos": Movement,
            "Importaciones": Import,
        }
    def send_data(self, business_id: int):
        with self.session_factory() as session:
            repository = MonitoringRepository(session)
            empleados = repository.count_employees(business_id)
            ventas = repository.count_sales(business_id)
            movimientos = repository.count_movements(business_id)
            importaciones = repository.count_imports(business_id)
            return {
                "success": True,
                "empleados": empleados,
                "ventas": ventas,
                "movimientos": movimientos,
                "importaciones": importaciones,
            }

    def check_database_health(self):
        results = []
        with self.session_factory() as session:
            repository = MonitoringRepository(session)
            for name, model in self.tables_to_check.items():
                try:
                    result = repository.check_table(model)
                except SQLAlchemyError:
                    session.rollback()
                    result = {
                        "table": model.__table__.name,
                        "status": "error",
                        "message": (
                            "Se recomienda revisar la conexión "
                            "y los registros en el servidor."
                        ),
                    }
                results.append({
                    "name": name,
                    **result,
                })
        return {
            "success": True,
            "tables": results,
        }
    def optimize_tables(self):
        with self.session_factory() as session:
            repository = MonitoringRepository(session)
            try:
                optimized = repository.optimize_tables()
            except SQLAlchemyError:
                session.rollback()
                optimized = False
        if optimized:
            return {
                "success": True,
                "message": (
                    "Se realizó la optimización de las tablas exitosamente."
                ),
            }
        return {
            "success": False,
            "message": "Ocurrió un error al optimizar las tablas.",
        }
