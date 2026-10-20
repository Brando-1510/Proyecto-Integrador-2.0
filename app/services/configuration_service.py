from app.models.business import TypeOfBusiness

class ConfigurationService:
    def __init__(self, configuration_repository):
        self.configuration_repository = configuration_repository
        self.session = configuration_repository.session
    def save_business_changes(
        self,business_id: int,business_name: str | None = None,
        type_of_business: TypeOfBusiness | None = None,description: str | None = None,
        categories_to_add: list[str] | None = None,categories_to_delete: list[int] | None = None,
    ):
        try:
            # Normalizar los valores opcionales.
            categories_to_add = categories_to_add or []
            categories_to_delete = categories_to_delete or []
            if business_name is not None:
                business_name = business_name.strip()
                if not business_name:
                    raise ValueError("El nombre del negocio no puede estar vacío.")
            if description is not None:
                description = description.strip()
            # Validar las categorías nuevas.
            categories_to_add = [
                name.strip() for name in categories_to_add
            ]
            if any(not name for name in categories_to_add):
                raise ValueError("Los nombres de las categorías no pueden estar vacíos.")
            if any(len(name) > 100 for name in categories_to_add):
                raise ValueError(
                    "Los nombres de las categorías no pueden superar los 100 caracteres."
                )
            nombres_normalizados = [
                name.casefold() for name in categories_to_add
            ]
            if len(set(nombres_normalizados)) != len(nombres_normalizados):
                raise ValueError("Hay categorías repetidas en la lista.")
            #*Modificar la información del negocio.
            business = self.configuration_repository.modify_business(
                business_id=business_id,
                business_name=business_name,
                type_of_business=type_of_business,
                description=description,
            )
            if business is None:
                raise ValueError("El negocio no existe.")
            #*Agregar las categorías nuevas.
            if categories_to_add:
                self.configuration_repository.add_categories(business_id=business_id,categories=categories_to_add,)
            #*Eliminar las categorías seleccionadas.
            for category_id in categories_to_delete:
                deleted = self.configuration_repository.delete_category(
                    business_id=business_id,category_id=category_id,
                )
                if not deleted:
                    raise ValueError(
                        "No se pudo eliminar una categoría. "
                        "Puede que no exista o que sea una categoría "
                        "del sistema."
                    )
            #*Confirmar todos los cambios en una sola transacción.
            self.session.commit()
            return {
                "success": True,
                "business": business,
                "message": (
                    "Información del negocio actualizada correctamente."
                ),
            }
        except ValueError as e:
            self.session.rollback()
            return {
                "success": False,
                "message": str(e),
            }
        except Exception:
            self.session.rollback()
            return {
                "success": False,
                "message": (
                    "Ocurrió un error al guardar los cambios."
                ),
            }