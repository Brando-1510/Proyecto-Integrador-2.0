from sqlalchemy import select, func, text
from app.models.movement import Movement
from app.models.sale import Sale
from app.models.business import Business
from app.models.imports import Import
from app.models.user_business import UserBusiness

class MonitoringRepository:
    def __init__(self, session):
        self.session = session
    def count_employees(self, business_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(UserBusiness)
            .where(UserBusiness.business_id == business_id)
        )
        return self.session.scalar(stmt) or 0
    def count_sales(self, business_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Sale)
            .where(Sale.business_id == business_id)
        )
        return self.session.scalar(stmt) or 0
    def count_movements(self, business_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Movement)
            .where(Movement.business_id == business_id)
        )
        return self.session.scalar(stmt) or 0
    def count_imports(self, business_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Import)
            .where(Import.business_id == business_id)
        )
        return self.session.scalar(stmt) or 0
    @staticmethod
    def _quote_identifier(name: str) -> str:
        return f"`{name.replace('`', '``')}`"
    def check_table(self, model) -> dict:
        table_name = model.__table__.name
        quoted_name = self._quote_identifier(table_name)
        stmt = text(f"CHECK TABLE {quoted_name}")
        result = self.session.execute(stmt).mappings().all()
        healthy = (
            bool(result)
            and any(
                row.get("Msg_type") == "status"
                and row.get("Msg_text") == "OK"
                for row in result
            )
            and not any(
                row.get("Msg_type") in ("error", "warning")
                for row in result
            )
        )
        return {
            "table": table_name,
            "status": "healthy" if healthy else "warning",
            "message": (
                "Sin problemas."
                if healthy
                else (
                    "La tabla presenta posibles problemas. "
                    "Se recomienda revisar su estado en el motor "
                    "de base de datos."
                )
            ),
        }
    def optimize_tables(self) -> bool:
        models = [
            UserBusiness,
            Business,
            Sale,
            Movement,
            Import,
        ]
        table_names = [
            self._quote_identifier(model.__table__.name)
            for model in models
        ]
        stmt = text(f"OPTIMIZE TABLE {', '.join(table_names)}")
        result = self.session.execute(stmt).mappings().all()
        if not result:
            return False
        for model in models:
            table_name = model.__table__.name
            table_results = [
                row
                for row in result
                if row.get("Table", "").split(".")[-1].strip("`")
                == table_name
            ]
            if not any(
                row.get("Msg_type") == "status" and row.get("Msg_text") == "OK"
                for row in table_results
            ):
                return False
            if any(
                row.get("Msg_type") in ("error", "warning")
                for row in table_results
            ):
                return False
        return True
