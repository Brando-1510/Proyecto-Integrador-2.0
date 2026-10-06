from app.models.sale import Sale
from sqlalchemy import select,func
from datetime import date

class SaleRepository:
    def __init__(self, session):
        self.session = session
    def create(self, sale: Sale):
        self.session.add(sale)
        self.session.flush()
        return sale
    def create_many(self, sales: list[Sale]):
        self.session.add_all(sales)
        self.session.flush()
        return sales
    #*Obtiene el monto total de las ventas en los ultimos 30 días
    def get_total_sales(self,business_id:int,start_date: date, end_date: date):
        stmt=(
            select(func.coalesce(func.sum(Sale.total), 0))
            .where(
                Sale.business_id==business_id,
                Sale.date.between(start_date,end_date)
            )
        )
        total_sales=self.session.scalar(stmt)
        return total_sales
    #*Gráfica de evolución
    def get_sales_evolution_last_30_days(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(Sale.date,func.sum(Sale.total))
            .where(
                Sale.business_id==business_id,
                Sale.date.between(start_date,end_date)
            )
            .group_by(Sale.date)
            .order_by(Sale.date)
        )
        resultado=self.session.execute(stmt).all()
        return resultado
    #*Para la sección de ventas recientes del home dashboard
    def get_recent_sales(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(Sale).where(
                Sale.business_id==business_id,
                Sale.date.between(start_date, end_date)
            )
            .order_by(Sale.date.desc()).limit(20)
        )
        resultado = self.session.scalars(stmt).all()
        return resultado
