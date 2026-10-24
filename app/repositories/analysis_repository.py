from app.models.sale import Sale
from app.models.movement import Movement
from app.models.category import Category
from app.models.movement import MovementType
from sqlalchemy import select,func,case,desc
from typing import List, Tuple
from decimal import Decimal
from datetime import date

class AnalysisRepository:
    def __init__(self,session):
        self.session=session
    #*Metodo relacionados al metodo movements
    #obtener total de ingresos y gastos
    def total_income_expenses(self,business_id:int,start_date:date,end_date:date)-> Tuple[Decimal, Decimal]:
        stmt=(
            select(
                func.coalesce(
                    func.sum(case((Movement.type==MovementType.INCOME,Movement.amount),else_=0)),0
                ).label("SumaIngresos"),
                func.coalesce(
                    func.sum(case((Movement.type==MovementType.EXPENSE,Movement.amount),else_=0)),0
                ).label("SumaGastos")
            )
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date)
            )
        )
        resultado = self.session.execute(stmt).one()
        return resultado.SumaIngresos, resultado.SumaGastos
    #Obtener ingresos y gastos agrupados por intervalo temporal
    def get_financial_performance(
        self,business_id:int,start_date:date,end_date:date
        ) -> List[Tuple[str, Decimal, Decimal]]:
        diferencia_dias = (end_date - start_date).days+1
        if diferencia_dias <= 31:
            intervalo_temporal = func.date_format(Movement.date, "%Y-%m-%d")
        else:
            intervalo_temporal = func.date_format(Movement.date, "%Y-%m")
        stmt=(
            select(
                intervalo_temporal.label("IntervaloTemporal"),
                func.coalesce(
                    func.sum(case((Movement.type==MovementType.INCOME,Movement.amount),else_=0)),0
                ).label("SumaIngresos"),
                func.coalesce(
                    func.sum(case((Movement.type==MovementType.EXPENSE,Movement.amount),else_=0)),0
                ).label("SumaGastos")
            )
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date)
            )
            .group_by(intervalo_temporal)
            .order_by(intervalo_temporal.asc())
        )
        resultados = self.session.execute(stmt).all()
        return resultados
    #Obtener gastos agrupados por categoría
    def get_expenses_category(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(
                Movement.category.label("CategoriaGastos"),
                func.coalesce(
                    func.sum(Movement.amount),0
                ).label("SumaGasto")
            )
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date),
                Movement.type==MovementType.EXPENSE
            )
            .group_by(Movement.category)
            .order_by(desc("SumaGasto"))
        )
        resultados = self.session.execute(stmt).all()
        return resultados
    #Obtener ingresos agrupados por categoría
    def get_income_category(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(
                Movement.category.label("CategoriaIngresos"),
                func.coalesce(
                    func.sum(Movement.amount),0
                ).label("SumaIngresos")
            )
            .where(
                Movement.business_id==business_id,
                Movement.date.between(start_date,end_date),
                Movement.type==MovementType.INCOME
            )
            .group_by(Movement.category)
            .order_by(desc("SumaIngresos"))
        )
        resultados = self.session.execute(stmt).all()
        return resultados
    #*Metodo relacionados al metodo sale
    def get_sales_indicators(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(
                func.count(Sale.sale_id).label("TotalVentas"),
                func.coalesce(func.sum(Sale.total),0).label("SumaTotalVentas")
            )
            .where(
                Sale.business_id==business_id,
                Sale.date.between(start_date,end_date)
            )
        )
        resultados = self.session.execute(stmt).one()
        return resultados
    #Obtener las ventas agrupadas por categoría
    def get_sales_category(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(
                Category.name.label("CategoriaNombre"),
                func.coalesce(func.sum(Sale.total),0).label("SumaVentas")
            )
            .join(
            Category,(Sale.category_id == Category.category_id)& (Sale.business_id == Category.business_id)
            )
            .where(
                Sale.business_id==business_id,
                Sale.date.between(start_date,end_date)
            )
            .group_by(Category.category_id, Category.name)
            .order_by(desc("SumaVentas"))
        )
        resultados = self.session.execute(stmt).all()
        return resultados
    #*Métodos relacionados al método de Imports
    #Obtener los importes individuales de venta
    def individual_sales_amount(self,business_id:int,start_date:date,end_date:date):
        stmt=(
            select(
                Sale.total.label("Total")
            )
            .where(
                Sale.business_id==business_id,
                Sale.date.between(start_date,end_date)
            )
        )
        resultados = self.session.execute(stmt).all()
        return resultados