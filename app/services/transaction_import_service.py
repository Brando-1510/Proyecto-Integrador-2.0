from app.models.sale import Sale
from app.models.movement import Movement,MovementType,PaymentMethod
from app.utils.category_utils import normalize_category_name

class TransactionImportService:
    def __init__(self,sale_repository,movement_repository,category_service):
        self.sale_repository = sale_repository
        self.movement_repository = movement_repository
        self.category_service = category_service

    def save_sales(self,df_sales,business_id: int,import_id: int,user_id: int):
        category_map = self.category_service.get_category_map(business_id)
        sales = []
        for _, row in df_sales.iterrows():
            category_name = normalize_category_name(row["Categoría"])
            category = category_map.get(category_name)
            if category is None:
                raise ValueError(
                    f"La categoría '{row['Categoría']}' "
                    f"no existe para este negocio."
                )
            sale = Sale(
                business_id=business_id,
                import_id=import_id,
                category_id=category.category_id,
                created_by=user_id,
                date=row["Fecha"].date(),
                product_service=row["Producto/Servicio"],
                quantity=row["Cantidad"],
                unit_price=row["Precio Unitario"],
                total=row["Total"]
            )
            sales.append(sale)
        return self.sale_repository.create_many(sales)

    def save_movements(self,df_movements,business_id: int,import_id: int,user_id: int):
        movements = []
        for _, row in df_movements.iterrows():
            movement = Movement(
                business_id=business_id,
                import_id=import_id,
                created_by=user_id,
                date=row["Fecha"].date(),
                type=MovementType(row["Tipo"]),
                category=row["Categoría"],
                description=row["Descripción"],
                amount=row["Monto"],
                payment_method=PaymentMethod(
                    row["Método de Pago"]
                )
            )
            movements.append(movement)
        return self.movement_repository.create_many(movements)