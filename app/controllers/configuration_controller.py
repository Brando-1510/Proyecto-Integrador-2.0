class ConfigurationController:
    def __init__(self, service):
        self.service = service

    def save_business_changes(
        self,
        business_id: int,
        business_name: str | None = None,
        type_of_business=None,
        description: str | None = None,
        categories_to_add: list[str] | None = None,
        categories_to_delete: list[int] | None = None,
    ):
        try:
            return self.service.save_business_changes(
                business_id=business_id,
                business_name=business_name,
                type_of_business=type_of_business,
                description=description,
                categories_to_add=categories_to_add,
                categories_to_delete=categories_to_delete,
            )

        except Exception:
            # Protección adicional ante errores inesperados.
            return {
                "success": False,
                "message": "No se pudo procesar la solicitud.",
            }