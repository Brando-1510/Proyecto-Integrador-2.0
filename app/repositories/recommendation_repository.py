from datetime import date
from decimal import Decimal
from sqlalchemy import select, func, case, desc
from app.models.movement import Movement, MovementType
from app.models.sale import Sale

class RecommendationRepository:
    def __init__(self, session):
        self.session = session
    #*G-01: Gastos agrupados por categoría
    def get_expenses_by_category(self,business_id: int,start_date: date,end_date: date) -> list[tuple[str, Decimal]]:
        stmt = (
            select(
                Movement.category,
                func.sum(Movement.amount).label("total_expenses")
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date),
                Movement.type == MovementType.EXPENSE
            )
            .group_by(Movement.category)
            .order_by(desc("total_expenses"))
        )
        return self.session.execute(stmt).all()

    #*G-02: Totales de ingresos y gastos
    def get_income_expense_totals(self,business_id: int,start_date: date,end_date: date) -> tuple[Decimal, Decimal]:
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.INCOME,Movement.amount),else_=0
                        )
                    ),0
                ).label("total_income"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.EXPENSE,Movement.amount),else_=0
                        )
                    ),0
                ).label("total_expenses")
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date)
            )
        )
        result = self.session.execute(stmt).one()
        return result.total_income, result.total_expenses

    #*V-01 y V-02: Importe total de ventas
    def get_sales_total(self,business_id: int,start_date: date,end_date: date) -> Decimal:
        stmt = (
            select(func.coalesce(func.sum(Sale.total),0))
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
        )
        return self.session.scalar(stmt)

    #*V-02: Importe vendido por producto
    def get_sales_by_product(self,business_id: int,start_date: date,end_date: date) -> list[tuple[str, Decimal]]:
        stmt = (
            select(
                Sale.product_service,
                func.sum(Sale.total).label("total_sold")
            )
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .group_by(Sale.product_service)
            .order_by(desc("total_sold"))
        )
        return self.session.execute(stmt).all()

    #*V-04: Cantidad vendida por producto
    def get_quantity_by_product(self,business_id: int,start_date: date,end_date: date) -> list[tuple[str, Decimal]]:
        stmt = (
            select(
                Sale.product_service,
                func.sum(Sale.quantity).label("total_quantity")
            )
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .group_by(Sale.product_service)
            .order_by(desc("total_quantity"))
        )
        return self.session.execute(stmt).all()

    #*V-06: Ventas agrupadas por día
    def get_daily_sales(self,business_id: int,start_date: date,end_date: date) -> list[tuple[date, Decimal]]:
        stmt = (
            select(
                Sale.date,
                func.sum(Sale.total).label("daily_total")
            )
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .group_by(Sale.date)
            .order_by(Sale.date.asc())
        )
        return self.session.execute(stmt).all()

    #*I-04: Registros individuales de ingresos
    def get_income_records_by_category(self,business_id: int,start_date: date,end_date: date) -> list[tuple[str, date, Decimal]]:
        stmt = (
            select(
                Movement.category,
                Movement.date,
                Movement.amount
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date),
                Movement.type == MovementType.INCOME
            )
            .order_by(
                Movement.category.asc(),
                Movement.date.asc(),
                Movement.movement_id.asc()
            )
        )
        return self.session.execute(stmt).all()