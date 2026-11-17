from app.prompts.financial_prompts import FinancialPromptBuilder
from datetime import date
from app.database.connection import SessionLocal
from app.repositories.financialContext_repository import FinancialContextRepository
from app.utils.date_utils import DateUtils

class AIRecommendationService:
    def __init__(self, session_factory=SessionLocal,cache_service=None):
        self.session_factory = session_factory
        self.cache_service = cache_service
    #*Preparar solicitudes para los análisis
    def prepare_analysis(self, datos: dict) -> str:
        metadata = self._get_analysis_metadata(datos)
        return self.prepare_analysis_from_metadata(metadata)

    #*Preparar solicitudes para el asistente financiero
    def prepare_assistant_prompt(self, datos: dict) -> str:
        business_id = datos.get("business_id")
        question = datos.get("question")
        if not isinstance(business_id, int) or business_id <= 0:
            raise ValueError("El negocio seleccionado no es válido.")
        if not question or not question.strip():
            raise ValueError("Debes escribir una pregunta.")
        context = self._get_global_context(business_id)
        return self._build_assistant_prompt(context, question)

    #*Obtener contexto financiero específico
    def _get_analysis_context(
        self,business_id: int,start_date: date,end_date: date
    ) -> dict:
        with self.session_factory() as session:
            repository = FinancialContextRepository(session)
            summary = repository.get_movement_summary(business_id, start_date, end_date)
            sales = repository.get_sales_summary(business_id, start_date, end_date)
            income_categories = repository.get_income_category(business_id, start_date, end_date)
            expense_categories = repository.get_expenses_category(business_id, start_date, end_date)
            sales_categories = repository.get_sales_category(business_id, start_date, end_date)
            sales_evolution = repository.get_sales_evolution(business_id, start_date, end_date)
            evolution = repository.get_financial_evolution(business_id, start_date, end_date)
            return {
                "summary": dict(summary._mapping),
                "sales": dict(sales._mapping),
                "income_categories": [
                    dict(row._mapping) for row in income_categories
                ],
                "expense_categories": [
                    dict(row._mapping) for row in expense_categories
                ],
                "sales_categories": [
                    dict(row._mapping) for row in sales_categories
                ],
                "sales_evolution": [dict(row._mapping) for row in sales_evolution],
                "evolution": [
                    dict(row._mapping) for row in evolution
                ]
            }

    #*Obtener contexto financiero global
    def _get_global_context(self, business_id: int) -> dict:
        with self.session_factory() as session:
            start_date, end_date = DateUtils.last_year()
            repository = FinancialContextRepository(session)
            summary = repository.get_movement_summary(business_id)
            sales = repository.get_sales_summary(business_id)
            income_categories = repository.get_income_category(business_id)
            expense_categories = repository.get_expenses_category(business_id)
            sales_categories = repository.get_sales_category(business_id)
            monthly_history = repository.get_monthly_financial_history(business_id, start_date, end_date)
            recent_transactions = repository.get_recent_transactions(business_id,limit=10)
            sales_evolution = repository.get_sales_evolution(business_id, start_date, end_date)
            return {
                "summary": dict(summary._mapping),
                "sales": dict(sales._mapping),
                "income_categories": [
                    dict(row._mapping) for row in income_categories
                ],
                "expense_categories": [
                    dict(row._mapping) for row in expense_categories
                ],
                "sales_categories": [
                    dict(row._mapping) for row in sales_categories
                ],
                "monthly_history": [
                    dict(row._mapping) for row in monthly_history
                ],
                "recent_transactions": [
                    dict(row._mapping) for row in recent_transactions
                ],
                "sales_evolution": [dict(row._mapping) for row in sales_evolution]
            }

    #*Obtener rango de fechas
    @staticmethod
    def _get_current_period(periodo: str) -> tuple[date, date]:
        periodos = {
            "Los Últimos 15 Días": DateUtils.last_15_days,
            "Este Mes": DateUtils.this_month,
            "Los Últimos 3 Meses": DateUtils.last_3_months,
            "Último Año": DateUtils.last_year
        }
        if periodo not in periodos:
            raise ValueError(f"Período no válido: {periodo}")
        start_date, end_date = periodos[periodo]()
        if start_date > end_date:
            raise ValueError("Rango de fechas no válido.")
        return start_date, end_date

    #*Obtener los metadatos
    def _get_analysis_metadata(self, datos: dict) -> dict:
        business_id = datos.get("business_id")
        analysis_type = datos.get("analysis_type")
        periodo = datos.get("periodo")
        if not isinstance(business_id, int) or business_id <= 0:
            raise ValueError("El negocio seleccionado no es válido.")
        if analysis_type not in (
            "General", "Ventas", "Ingresos", "Gastos"
        ):
            raise ValueError("Tipo de análisis no válido.")
        start_date, end_date = self._get_current_period(periodo)
        return {
            "business_id": business_id,
            "analysis_type": analysis_type,
            "start_date": start_date,
            "end_date": end_date
        }

    #*Metodos de administración de la caché
    def get_analysis_version(self, business_id: int) -> int | None:
        if self.cache_service is None:
            return None
        return self.cache_service.get_version(business_id)

    def get_cached_analysis(self,metadata: dict,version: int) -> str | None:
        if self.cache_service is None or version is None:
            return None
        return self.cache_service.get_analysis(
            business_id=metadata["business_id"],
            version=version,
            analysis_type=metadata["analysis_type"],
            start_date=metadata["start_date"],
            end_date=metadata["end_date"]
        )

    def is_analysis_version_current(self,business_id: int,expected_version: int) -> bool:
        if self.cache_service is None or expected_version is None:
            return False
        current_version = self.cache_service.get_version(business_id)
        return current_version == expected_version

    def save_cached_analysis(self,metadata: dict,version: int,response: str) -> bool:
        if self.cache_service is None or version is None:
            return False
        return self.cache_service.set_analysis(
            business_id=metadata["business_id"],
            version=version,
            analysis_type=metadata["analysis_type"],
            start_date=metadata["start_date"],
            end_date=metadata["end_date"],
            response=response
        )
    def get_analysis_metadata(self, datos: dict) -> dict:
        return self._get_analysis_metadata(datos)

    def prepare_analysis_from_metadata(self, metadata: dict) -> str:
        business_id = metadata["business_id"]
        analysis_type = metadata["analysis_type"]
        start_date = metadata["start_date"]
        end_date = metadata["end_date"]
        context = self._get_analysis_context(business_id, start_date, end_date)
        if analysis_type == "Ventas":
            return self._build_sales_prompt(context, start_date, end_date)
        elif analysis_type == "Ingresos":
            return self._build_income_prompt(context, start_date, end_date)
        elif analysis_type == "Gastos":
            return self._build_expenses_prompt(context, start_date, end_date)
        return self._build_general_prompt(context, start_date, end_date)

    #*Construcción de prompts
    def _build_expenses_prompt(self, context: dict, start_date: date, end_date: date) -> str:
        return FinancialPromptBuilder.build_expenses_prompt(context, start_date, end_date)
    def _build_income_prompt(self, context: dict, start_date: date, end_date: date) -> str:
        return FinancialPromptBuilder.build_income_prompt(context, start_date, end_date)
    def _build_general_prompt(self, context: dict, start_date: date, end_date: date) -> str:
        return FinancialPromptBuilder.build_general_prompt(context, start_date, end_date)
    def _build_assistant_prompt(self, context: dict, question: str) -> str:
        return FinancialPromptBuilder.build_assistant_prompt(context, question)
    def _build_sales_prompt(self, context: dict, start_date: date, end_date: date) -> str:
        return FinancialPromptBuilder.build_sales_prompt(context, start_date, end_date)
