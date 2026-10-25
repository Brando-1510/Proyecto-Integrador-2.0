from pandas import DataFrame
from app.database.connection import SessionLocal
from app.models.sale import Sale
from app.models.movement import Movement,MovementType,PaymentMethod,IncomeCategory,ExpenseCategory
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
from app.utils.category_utils import normalize_category_name
from app.errors.import_errors import CategoryNotFoundError

class TransactionImportService:
    def __init__(self,import_service,category_service,session_factory=SessionLocal,):
        self.session_factory = session_factory
        self.import_service = import_service
        self.category_service = category_service
    def save_import_data(
        self,user_id: int,business_id: int,file_path: str,file_name: str,df_sales: DataFrame | None,
        df_movements: DataFrame | None,categories_to_create: list[str] | None = None,
    ):
        if (
            (df_sales is None or df_sales.empty)and (df_movements is None or df_movements.empty)
        ):
            raise ValueError("No hay datos para guardar en la importación.")

        with self.session_factory.begin() as session:
            sale_repository = SaleRepository(session)
            movement_repository = MovementRepository(session)
            if categories_to_create:
                self.category_service.create_missing_categories(
                    business_id=business_id,category_names=categories_to_create,session=session,
                )
            category_map = self._get_sales_category_map(
                df_sales=df_sales,
                business_id=business_id,
                session=session,
            )
            import_created = self.import_service.save_import(
                user_id=user_id,
                business_id=business_id,
                file_path=file_path,
                file_name=file_name,
                session=session,
            )
            #*Guardar las ventas.
            self.save_sales(
                df_sales=df_sales,
                business_id=business_id,
                import_id=import_created.import_id,
                user_id=user_id,
                category_map=category_map,
                sale_repository=sale_repository,
            )
            #*Guardar los movimientos.
            self.save_movements(
                df_movements=df_movements,
                business_id=business_id,
                import_id=import_created.import_id,
                user_id=user_id,
                movement_repository=movement_repository,
            )
            return {
                "import_id": import_created.import_id,
                "file_name": import_created.file_name,
                "business_id": import_created.business_id,
            }

    def _get_sales_category_map(
        self,df_sales: DataFrame | None,business_id: int,session,
    ) -> dict:
        if df_sales is None or df_sales.empty:
            return {}
        category_map = self.category_service.get_category_map(
            business_id=business_id,session=session,
        )
        missing_categories = {}
        for _, row in df_sales.iterrows():
            original_name = str(row["Categoría"]).strip()
            normalized_name = normalize_category_name(original_name)
            if normalized_name not in category_map:
                missing_categories.setdefault(normalized_name,original_name,)
        if missing_categories:
            raise CategoryNotFoundError(list(missing_categories.values()))
        return category_map

    def save_sales(
        self,df_sales: DataFrame | None,business_id: int,import_id: int,
        user_id: int,category_map: dict,sale_repository: SaleRepository,
    ):
        if df_sales is None or df_sales.empty:
            return []
        sales = []
        for _, row in df_sales.iterrows():
            category_name = normalize_category_name(row["Categoría"])
            category = category_map[category_name]
            sale = Sale(
                business_id=business_id,
                import_id=import_id,
                category_id=category.category_id,
                created_by=user_id,
                date=row["Fecha"].date(),
                product_service=row["Producto/Servicio"],
                quantity=row["Cantidad"],
                unit_price=row["Precio Unitario"],
                total=row["Total"],
            )
            sales.append(sale)
        return sale_repository.create_many(sales)

    def save_movements(
        self,df_movements: DataFrame | None,business_id: int,import_id: int,
        user_id: int,movement_repository: MovementRepository,
    ):
        if df_movements is None or df_movements.empty:
            return []
        movements = []
        for _, row in df_movements.iterrows():
            movement_type = self._get_enum_member(MovementType,row["Tipo"],)
            payment_method = self._get_enum_member(PaymentMethod,row["Método de Pago"],)
            category_enum = (
                IncomeCategory
                if movement_type == MovementType.INCOME
                else ExpenseCategory
            )
            category = self._get_enum_member(category_enum,row["Categoría"],)
            movement = Movement(
                business_id=business_id,
                import_id=import_id,
                created_by=user_id,
                date=row["Fecha"].date(),
                type=movement_type,
                category=category.value,
                description=row["Descripción"],
                amount=row["Monto"],
                payment_method=payment_method,
            )
            movements.append(movement)
        return movement_repository.create_many(movements)

    @staticmethod
    def _get_enum_member(enum_class, value):
        normalized_value = str(value).strip().casefold()
        for item in enum_class:
            if item.value.casefold() == normalized_value:
                return item
        raise ValueError(f"El valor '{value}' no pertenece al enum {enum_class.__name__}.")
