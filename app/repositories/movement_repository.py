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
    def get_income_last_30_days(self,business_id:int,start_date: date, end_date: date):
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
    def get_expenses_last_30_days(self,business_id:int,start_date: date, end_date: date):
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
    def get_recent_movements(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(Movement).where(
                Movement.business_id==business_id,
                Movement.date.between(start_date, end_date)
                )
            .order_by(Movement.date.desc()).limit(20)
        )
        resultado = self.session.scalars(stmt).all()
        return resultado
    #*Obtener la utilidad
    def get_utility(self,business_id:int,start_date:date,end_date:date):
        suma_ingresos=func.sum(case((Movement.type=="Ingreso",Movement.amount),else_=0))
        suma_gastos=func.sum(case((Movement.type=="Gasto",Movement.amount),else_=0))
        stmt=(
            (suma_ingresos-suma_gastos)
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date),
            )
        )
        resultado=self.session.execute(stmt).first()
        return resultado