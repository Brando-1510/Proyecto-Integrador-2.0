from sqlalchemy import select, func,text
from app.models.movement import Movement, MovementType
from app.models.sale import Sale
from app.models.users import Users
from app.models.business import Business
from app.models.imports import Import
from app.models.user_business import UserBusiness
from sqlalchemy.exc import SQLAlchemyError

class MonitoringRepository:
    def __init__(self,session):
        self.session=session
    def count_employees(self,business_id:int):
        stmt= (
            select(func.count())
            .select_from(UserBusiness)
            .where(UserBusiness.business_id==business_id)
        )
        return self.session.scalar(stmt)
    def count_sales(self,business_id:int):
        stmt= (
            select(func.count())
            .select_from(Sale)
            .where(Sale.business_id==business_id)
        )
        return self.session.scalar(stmt)
    def count_movements(self,business_id:int):
        stmt= (
            select(func.count())
            .select_from(Movement)
            .where(Movement.business_id==business_id)
        )
        return self.session.scalar(stmt)
    def count_imports(self,business_id:int):
        stmt= (
            select(func.count())
            .select_from(Import)
            .where(Import.business_id==business_id)
        )
        return self.session.scalar(stmt)

    def check_table(self, model) -> dict:
        table_name = model.__table__.name
        quoted_name = f"`{table_name.replace('`', '``')}`"
        try:
            stmt = text(f"CHECK TABLE {quoted_name}")
            result = self.session.execute(stmt).mappings().all()
            healthy = bool(result) and any(
                row.get("Msg_type") == "status"
                and row.get("Msg_text") == "OK"
                for row in result
            ) and not any(
                row.get("Msg_type") in ("error", "warning")
                for row in result
            )
            return {
                "table": table_name,
                "status": "healthy" if healthy else "warning",
                "message": (
                    "Sin problemas."
                    if healthy
                    else "La tabla presenta posibles problemas. "
                        "Se recomienda revisar su estado en el motor "
                        "de base de datos."
                )
            }
        except SQLAlchemyError:
            self.session.rollback()
            return {
                "table": table_name,
                "status": "error",
                "message": (
                    "Se recomienda revisar la conexión y los registros en el servidor"
                )
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
            f"`{model.__table__.name.replace('`', '``')}`"
            for model in models
        ]
        try:
            stmt = text(f"OPTIMIZE TABLE {', '.join(table_names)}")
            result = self.session.execute(stmt).mappings().all()
            if not result:
                return False
            for model in models:
                table_name = model.__table__.name
                table_results = [
                    row for row in result
                    if row.get("Table", "").split(".")[-1].strip("`")
                    == table_name
                ]
                if not any(
                    row.get("Msg_type") == "status"
                    and row.get("Msg_text") == "OK"
                    for row in table_results
                ):
                    return False
                if any(
                    row.get("Msg_type") in ("error", "warning")
                    for row in table_results
                ):
                    return False
            return True
        except SQLAlchemyError:
            self.session.rollback()
            return False