from app.models.movement import Movement
from sqlalchemy import select,func,case
from datetime import date

class MovementRepository:
    def __init__(self, session):
        self.session = session
    def create(self, movement: Movement):
        self.session.add(movement)
        self.session.flush()
        return movement
    def create_many(self, movements: list[Movement]):
        self.session.add_all(movements)
        self.session.flush()
        return movements
    #*Obtiene el monto total de los movimientos de ingresos en los ultimos 30 dias
    def get_income(self,business_id:int,start_date: date, end_date: date):
        stmt=(
            select(func.coalesce(func.sum(Movement.amount), 0))
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date),
                Movement.type=="Ingreso"
            )
        )
        total_income=self.session.scalar(stmt)
        return total_income
    #*Obtiene el monto total de los movimientos de gastos en los ultimos 30 dias
    def get_expenses(self,business_id:int,start_date: date, end_date: date):
        stmt=(
            select(func.coalesce(func.sum(Movement.amount), 0))
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date),
                Movement.type=="Gasto"
            )
        )
        total_expenses=self.session.scalar(stmt)
        return total_expenses
    #*Para la sección de movimientos recientes del home dashboard
    def get_movements(
        self,business_id:int,start_date:date,end_date:date,movement_type:str | None=None,
        description:str | None=None,limit: int | None = 20,
        ):
        stmt=(
            select(Movement).where(
                Movement.business_id==business_id,
                Movement.date.between(start_date, end_date)
                )
            .order_by(Movement.date.desc())
        )
        if movement_type is not None:
            stmt=stmt.where(Movement.type==movement_type)
        if description is not None:
            stmt=stmt.where(Movement.description.like(description))
        if limit is not None:
            stmt=stmt.limit(limit)
        resultado = self.session.scalars(stmt).all()
        return resultado
