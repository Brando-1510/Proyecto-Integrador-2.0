
from app.database.connection import SessionLocal
from app.utils.date_utils import DateUtils
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.import_repository import ImportRepository


class ConsultationService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def get_sales(self, datos):
        start_date, end_date = self.obtener_rango_fechas(datos)

        with self.session_factory() as session:
            sale_repository = SaleRepository(session)

            ventas = sale_repository.get_sales(
                datos["business_id"],
                start_date,
                end_date,
                datos.get("categoria_id"),
                limit=None,
            )

        return {
            "success": True,
            "fecha_inicio": start_date,
            "fecha_final": end_date,
            "ventas": ventas,
        }

    def get_movements(self, datos):
        start_date, end_date = self.obtener_rango_fechas(datos)

        with self.session_factory() as session:
            movement_repository = MovementRepository(session)

            movimientos = movement_repository.get_movements(
                datos["business_id"],
                start_date,
                end_date,
                datos.get("tipo_movimiento"),
                datos.get("descripcion"),
                limit=None,
            )

        return {
            "success": True,
            "fecha_inicio": start_date,
            "fecha_final": end_date,
            "movimientos": movimientos,
        }

    def get_imports(self, datos):
        start_date, end_date = self.obtener_rango_fechas(datos)

        first_date, second_date = DateUtils.to_datetime_range(
            start_date,
            end_date,
        )

        with self.session_factory() as session:
            import_repository = ImportRepository(session)

            importaciones = import_repository.get_imports(
                datos["business_id"],
                first_date,
                second_date,
                datos.get("nombre"),
            )

        return {
            "success": True,
            "fecha_inicio": start_date,
            "fecha_final": end_date,
            "importaciones": importaciones,
        }

    def obtener_rango_fechas(self, datos):
        periodo = datos["periodo"]

        if periodo == "Personalizado":
            start_date = datos.get("rango_inicio")
            end_date = datos.get("rango_final")

            if start_date is None or end_date is None:
                raise ValueError("Debes seleccionar ambas fechas.")

        elif periodo == "Esta Semana":
            start_date, end_date = DateUtils.this_week()

        elif periodo == "Este Mes":
            start_date, end_date = DateUtils.last_30_days()

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
