
from app.database.connection import SessionLocal
from app.models.business import TypeOfBusiness
from app.models.user_business import Role
from app.repositories.configuration_repository import ConfigurationRepository


class ConfigurationService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    # ---------------------------------------------------------
    # CONFIGURACIÓN DEL NEGOCIO
    # ---------------------------------------------------------

    def save_business_changes(
        self,
        business_id: int,
        business_name: str | None = None,
        type_of_business: TypeOfBusiness | None = None,
        description: str | None = None,
        categories_to_add: list[str] | None = None,
        categories_to_delete: list[int] | None = None,
    ):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            try:
                # Normalizar valores opcionales.
                categories_to_add = categories_to_add or []
                categories_to_delete = categories_to_delete or []

                if business_name is not None:
                    business_name = business_name.strip()

                    if not business_name:
                        raise ValueError(
                            "El nombre del negocio no puede estar vacío."
                        )

                if description is not None:
                    description = description.strip()

                # Validar las categorías nuevas.
                categories_to_add = [
                    name.strip() for name in categories_to_add
                ]

                if any(not name for name in categories_to_add):
                    raise ValueError(
                        "Los nombres de las categorías no pueden estar vacíos."
                    )

                if any(len(name) > 100 for name in categories_to_add):
                    raise ValueError(
                        "Los nombres de las categorías no pueden "
                        "superar los 100 caracteres."
                    )

                nombres_normalizados = [
                    name.casefold() for name in categories_to_add
                ]

                if len(set(nombres_normalizados)) != len(nombres_normalizados):
                    raise ValueError(
                        "Hay categorías repetidas en la lista."
                    )

                # Modificar la información del negocio.
                business = repository.modify_business(
                    business_id=business_id,
                    business_name=business_name,
                    type_of_business=type_of_business,
                    description=description,
                )

                if business is None:
                    raise ValueError("El negocio no existe.")

                # Agregar categorías nuevas.
                if categories_to_add:
                    repository.add_categories(
                        business_id=business_id,
                        categories=categories_to_add,
                    )

                # Eliminar categorías seleccionadas.
                for category_id in categories_to_delete:
                    deleted = repository.delete_category(
                        business_id=business_id,
                        category_id=category_id,
                    )

                    if not deleted:
                        raise ValueError(
                            "No se pudo eliminar una categoría. "
                            "Puede que no exista o que sea una "
                            "categoría del sistema."
                        )

                # Confirmar todos los cambios en una sola transacción.
                session.commit()

                business_actualizado = repository.get_business(business_id)

                if business_actualizado is None:
                    raise RuntimeError(
                        "No se pudo recuperar el negocio actualizado."
                    )

                session.expunge(business_actualizado)

                return {
                    "success": True,
                    "business": business_actualizado,
                    "message": (
                        "Información del negocio actualizada correctamente."
                    ),
                }

            except ValueError as e:
                session.rollback()
                return {
                    "success": False,
                    "message": str(e),
                }

            except Exception:
                session.rollback()
                return {
                    "success": False,
                    "message": (
                        "Ocurrió un error al guardar los cambios."
                    ),
                }

    # ---------------------------------------------------------
    # CONSULTAS DE USUARIOS Y EMPLEADOS
    # ---------------------------------------------------------

    def get_users(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            if datos["tipo"] == "correo":
                return repository.get_users(
                    email=datos["texto"]
                )

            return repository.get_users(
                name=datos["texto"]
            )

    def get_employees(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            if datos["tipos"] == "correo":
                return repository.get_employees(
                    business_id=datos["business_id"],
                    email=datos["texto"],
                )

            return repository.get_employees(
                business_id=datos["business_id"],
                name=datos["texto"],
            )

    # ---------------------------------------------------------
    # VINCULACIÓN DE USUARIOS
    # ---------------------------------------------------------

    def link_user(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            try:
                user_id = repository.get_user_id(datos["correo"])

                if not user_id:
                    raise ValueError(
                        "No existe un correo vinculado a ese usuario."
                    )

                if repository.get_userBusiness_relationship(
                    user_id, datos["business_id"]
                ):
                    raise ValueError(
                        "El usuario ya está vinculado al negocio."
                    )

                # Normalizar y validar el rol.
                rol = datos["rol"]

                if not isinstance(rol, Role):
                    try:
                        rol = Role(rol)
                    except (ValueError, TypeError):
                        raise ValueError(
                            "El rol seleccionado no es válido."
                        )

                if rol == Role.ADMIN:
                    raise ValueError(
                        "No se puede asignar el rol de administrador técnico."
                    )

                repository.link_user_to_business(
                    user_id=user_id,
                    business_id=datos["business_id"],
                    role=rol,
                )

                session.commit()
                return True

            except Exception:
                session.rollback()
                raise

    def delete_employee(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            try:
                user_id = repository.get_user_id(datos["correo"])

                if not user_id:
                    raise ValueError(
                        "No existe un correo vinculado a ese usuario."
                    )

                business_id = datos["business_id"]

                if not repository.get_userBusiness_relationship(
                    user_id, business_id
                ):
                    raise ValueError(
                        "El usuario no está vinculado al negocio."
                    )

                if repository.is_creator(user_id, business_id):
                    raise ValueError(
                        "No puede eliminar al creador del negocio."
                    )

                if repository.is_admin(user_id):
                    raise ValueError(
                        "No se puede desvincular a un administrador "
                        "técnico de un negocio."
                    )

                eliminado = repository.unlink_user_from_business(
                    user_id, business_id
                )

                if not eliminado:
                    raise ValueError(
                        "No se pudo desvincular al usuario del negocio."
                    )

                session.commit()
                return True

            except Exception:
                session.rollback()
                raise

    # ---------------------------------------------------------
    # OPERACIONES CRÍTICAS
    # ---------------------------------------------------------

    def delete_import(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            try:
                resultado = repository.delete_import(
                    datos["business_id"],
                    datos["import_id"],
                )

                if resultado:
                    session.commit()
                else:
                    session.rollback()

                return resultado

            except Exception:
                session.rollback()
                raise

    def delete_business(self, datos):
        with self.session_factory() as session:
            repository = ConfigurationRepository(session)

            try:
                if not repository.is_creator(
                    datos["user_id"],
                    datos["business_id"],
                ):
                    raise ValueError(
                        "Solo el creador puede eliminar el negocio."
                    )

                resultado = repository.delete_business(
                    datos["business_id"]
                )

                if resultado:
                    session.commit()
                else:
                    session.rollback()

                return resultado

            except Exception:
                session.rollback()
                raise
