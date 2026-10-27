from app.models.movement import Movement
from sqlalchemy import select,func,case
from datetime import date
from app.models.movement import Movement, MovementType

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
            .order_by(Movement.date.desc(),Movement.movement_id.desc(),)
        )
        if movement_type is not None:
            stmt=stmt.where(Movement.type==movement_type)
        if description is not None:
            stmt=stmt.where(Movement.description.like(f"%{description.strip()}%"))
        if limit is not None:
            stmt=stmt.limit(limit)
        resultado = self.session.scalars(stmt).all()
        return resultado

    def get_movements_by_category(
        self,business_id: int,start_date: date,end_date: date,movement_type: MovementType,
    ):
        stmt = (
            select(
                Movement.category,
                func.sum(Movement.amount).label("total"),
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date),
                Movement.type == movement_type,
            )
            .group_by(Movement.category)
            .order_by(func.sum(Movement.amount).desc())
        )
        return self.session.execute(stmt).all()


    def get_movement_evolution(self,business_id: int,start_date: date,end_date: date,
    ):
        stmt = (
            select(
                Movement.date,
                Movement.type,
                func.sum(Movement.amount).label("total"),
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date),
            )
            .group_by(Movement.date, Movement.type)
            .order_by(Movement.date)
        )
        return self.session.execute(stmt).all()

