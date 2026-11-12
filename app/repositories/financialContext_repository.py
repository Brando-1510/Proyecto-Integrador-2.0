from app.models.sale import Sale
from app.models.movement import Movement, MovementType
from app.models.category import Category
from sqlalchemy import select, func, case, desc,literal,cast,String
from datetime import date
from typing import Optional

class FinancialContextRepository:
    def __init__(self, session):
        self.session = session
    #*Métodos auxiliares para los filtros temporales
    def _date_filters(self, model, start_date, end_date):
        if (start_date is None) != (end_date is None):
            raise ValueError("Debes proporcionar ambas fechas.")
        if start_date is not None and start_date > end_date:
            raise ValueError("Rango de fechas no válido.")
        filters = []
        if start_date is not None:
            filters.append(model.date >= start_date)
        if end_date is not None:
            filters.append(model.date <= end_date)
        return filters

    #*Métodos relacionados con los movimientos
    # Obtener resumen financiero de ingresos y gastos
    def get_movement_summary(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.INCOME,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("TotalIngresos"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.EXPENSE,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("TotalGastos"),
                func.count(Movement.type).label("TotalMovimientos"),
                func.sum(
                    case(
                        (Movement.type == MovementType.INCOME, 1),
                        else_=0
                    )
                ).label("CantidadIngresos"),
                func.sum(
                    case(
                        (Movement.type == MovementType.EXPENSE, 1),
                        else_=0
                    )
                ).label("CantidadGastos")
            )
            .where(
                Movement.business_id == business_id,
                *self._date_filters(Movement, start_date, end_date)
            )
        )
        resultado = self.session.execute(stmt).one()
        return resultado

    # Obtener ingresos agrupados por categoría
    def get_income_category(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        stmt = (
            select(
                Movement.category.label("Categoria"),
                func.coalesce(
                    func.sum(Movement.amount), 0
                ).label("TotalIngresos")
            )
            .where(
                Movement.business_id == business_id,
                Movement.type == MovementType.INCOME,
                *self._date_filters(Movement, start_date, end_date)
            )
            .group_by(Movement.category)
            .order_by(desc("TotalIngresos"))
        )
        return self.session.execute(stmt).all()

    # Obtener gastos agrupados por categoría
    def get_expenses_category(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        stmt = (
            select(
                Movement.category.label("Categoria"),
                func.coalesce(
                    func.sum(Movement.amount), 0
                ).label("TotalGastos")
            )
            .where(
                Movement.business_id == business_id,
                Movement.type == MovementType.EXPENSE,
                *self._date_filters(Movement, start_date, end_date)
            )
            .group_by(Movement.category)
            .order_by(desc("TotalGastos"))
        )
        return self.session.execute(stmt).all()

    #*Métodos relacionados con las ventas
    # Obtener indicadores generales de ventas
    def get_sales_summary(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        stmt = (
            select(
                func.count(Sale.sale_id).label("CantidadVentas"),
                func.coalesce(
                    func.sum(Sale.total), 0
                ).label("TotalVentas"),
                func.coalesce(
                    func.avg(Sale.total), 0
                ).label("PromedioVenta")
            )
            .where(
                Sale.business_id == business_id,
                *self._date_filters(Sale, start_date, end_date)
            )
        )
        return self.session.execute(stmt).one()

    # Obtener ventas agrupadas por categoría
    def get_sales_category(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        stmt = (
            select(
                Category.name.label("Categoria"),
                func.coalesce(
                    func.sum(Sale.total), 0
                ).label("TotalVentas")
            )
            .join(
                Category,
                (Sale.category_id == Category.category_id) &
                (Sale.business_id == Category.business_id)
            )
            .where(
                Sale.business_id == business_id,
                *self._date_filters(Sale, start_date, end_date)
            )
            .group_by(Category.category_id, Category.name)
            .order_by(desc("TotalVentas"))
        )
        return self.session.execute(stmt).all()

    # Obtener evolución de las ventas
    def get_sales_evolution(
        self, business_id: int, start_date: date, end_date: date
    ):
        if start_date > end_date:
            raise ValueError("Rango de fechas no válido.")
        diferencia_dias = (end_date - start_date).days + 1
        if diferencia_dias <= 31:
            intervalo = func.date_format(Sale.date, "%Y-%m-%d")
        else:
            intervalo = func.date_format(Sale.date, "%Y-%m")
        stmt = (
            select(
                intervalo.label("Periodo"),
                func.coalesce(
                    func.sum(Sale.total), 0
                ).label("Ventas")
            )
            .where(
                Sale.business_id == business_id,
                Sale.date.between(start_date, end_date)
            )
            .group_by(intervalo)
            .order_by(intervalo.asc())
        )
        return self.session.execute(stmt).all()

    #*Métodos relacionados con el comportamiento financiero
    # Obtener evolución de ingresos y gastos
    def get_financial_evolution(
        self,business_id: int,start_date: date,end_date: date
    ):
        diferencia_dias = (end_date - start_date).days + 1
        if diferencia_dias <= 31:
            intervalo = func.date_format(Movement.date, "%Y-%m-%d")
        else:
            intervalo = func.date_format(Movement.date, "%Y-%m")
        stmt = (
            select(
                intervalo.label("Periodo"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.INCOME,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("Ingresos"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.EXPENSE,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("Gastos")
            )
            .where(
                Movement.business_id == business_id,
                Movement.date.between(start_date, end_date)
            )
            .group_by(intervalo)
            .order_by(intervalo.asc())
        )
        return self.session.execute(stmt).all()

    # Obtener historial financiero mensual
    def get_monthly_financial_history(
        self,business_id: int,start_date: Optional[date] = None,end_date: Optional[date] = None
    ):
        intervalo = func.date_format(Movement.date, "%Y-%m")
        stmt = (
            select(
                intervalo.label("Periodo"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.INCOME,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("Ingresos"),
                func.coalesce(
                    func.sum(
                        case(
                            (Movement.type == MovementType.EXPENSE,
                            Movement.amount),
                            else_=0
                        )
                    ), 0
                ).label("Gastos")
            )
            .where(
                Movement.business_id == business_id,
                *self._date_filters(Movement, start_date, end_date)
            )
            .group_by(intervalo)
            .order_by(intervalo.asc())
        )
        return self.session.execute(stmt).all()

# Obtener las transacciones más recientes
    def get_recent_transactions(self, business_id: int, limit: int = 10):
        if limit < 1:
            raise ValueError("El límite debe ser mayor que cero.")
        movements = (
            select(
                Movement.date.label("Fecha"),
                cast(Movement.type, String).label("Tipo"),
                Movement.category.label("Categoria"),
                Movement.amount.label("Monto")
            )
            .where(Movement.business_id == business_id)
        )
        sales = (
            select(
                Sale.date.label("Fecha"),
                literal("VENTA", type_=String()).label("Tipo"),
                Category.name.label("Categoria"),
                Sale.total.label("Monto")
            )
            .join(
                Category,
                (Sale.category_id == Category.category_id) &
                (Sale.business_id == Category.business_id)
            )
            .where(Sale.business_id == business_id)
        )
        transactions = movements.union_all(sales).subquery()
        stmt = (
            select(
                transactions.c.Fecha,
                transactions.c.Tipo,
                transactions.c.Categoria,
                transactions.c.Monto
            )
            .order_by(transactions.c.Fecha.desc())
            .limit(limit)
        )
        return self.session.execute(stmt).all()
