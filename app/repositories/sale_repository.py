
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.models.sale import Sale


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

    # Obtiene el monto total de las ventas en un período.
    def get_total_sales(
        self,
        business_id: int,
        start_date: date,
        end_date: date
    ):
        stmt = (
            select(func.coalesce(func.sum(Sale.total), 0))
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
        )

        return self.session.scalar(stmt)

    # Datos para la gráfica de evolución de ventas.
    def get_sales_evolution_last_30_days(
        self,
        business_id: int,
        start_date: date,
        end_date: date
    ):
        stmt = (
            select(Sale.date, func.sum(Sale.total))
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .group_by(Sale.date)
            .order_by(Sale.date)
        )

        return self.session.execute(stmt).all()

    # Consulta las ventas para la tabla de movimientos/ventas.
    def get_sales(
        self,
        business_id: int,
        start_date: date,
        end_date: date,
        category: int | None = None,
        limit: int | None = 20
    ):
        stmt = (
            select(Sale)
            .options(joinedload(Sale.category))
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .order_by(
                Sale.date.desc(),
                Sale.sale_id.desc()
            )
        )

        if category is not None:
            stmt = stmt.where(Sale.category_id == category)

        if limit is not None:
            stmt = stmt.limit(limit)

        return self.session.scalars(stmt).all()
