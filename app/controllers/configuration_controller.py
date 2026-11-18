from app.services.configuration_service import ConfigurationService
from app.utils.validators import ValidadoresDatos as VD
from app.models.user_business import Role
class ConfigurationController:
    def __init__(self, service:ConfigurationService):
        self.service = service
    def save_business_changes(
        self,business_id: int,business_name: str | None = None,type_of_business=None,
        description: str | None = None,categories_to_add: list[str] | None = None,
        categories_to_delete: list[int] | None = None,
        actor_user_id: int | None = None,
    ):
        try:
            return self.service.save_business_changes(
                business_id=business_id,
                actor_user_id=actor_user_id,
                business_name=business_name,
                type_of_business=type_of_business,
                description=description,
                categories_to_add=categories_to_add,
                categories_to_delete=categories_to_delete,
            )
        except Exception:
            return {
                "success": False,
                "message": "No se pudo procesar la solicitud.",
            }
    def get_users(self,texto,business_id,actor_user_id):
        tipo ="correo" if VD.validar_correo(texto) else "nombre"
        datos= {
            "tipo":tipo,
            "texto": texto,
            "business_id":business_id,
            "actor_user_id":actor_user_id,
        }
        try:
            usuarios=self.service.get_users(datos)
            return {"success": True, "usuarios": usuarios}
        except PermissionError as e:
            return {"success": False, "usuarios": [], "message": str(e)}
    def get_employees(self,texto,business_id,actor_user_id):
        tipos ="correo" if VD.validar_correo(texto) else "nombre"
        datos={
            "tipos":tipos,
            "texto":texto,
            "business_id":business_id,
            "actor_user_id":actor_user_id,
        }
        try:
            empleados=self.service.get_employees(datos)
            return {"success": True, "empleados": empleados}
        except PermissionError as e:
            return {"success": False, "empleados": [], "message": str(e)}
    def link_user(self,business_id,correo,rol,actor_user_id):
        datos={
            "business_id":business_id,
            "correo":correo,
            "rol":rol,
            "actor_user_id":actor_user_id,
        }
        try:
            self.service.link_user(datos)
            return {
                "success":True,
                "message":"El usuario fue vinculado correctamente"
            }
        except Exception as e:
            return {
                "success":False,
                "message": f"{e}"
            }
    def unlink_user(self,business_id,correo,actor_user_id):
        datos={
            "business_id":business_id,
            "correo":correo,
            "actor_user_id":actor_user_id,
        }
        try:
            self.service.delete_employee(datos)
            return {
                "success":True,
                "message":"El usuario fue desvinculado correctamente"
            }
        except Exception as e:
            return {
                "success":False,
                "message": f"{e}"
            }
    def delete_import(self,business_id,import_id,actor_user_id):
        datos={
            "business_id":business_id,
            "import_id":import_id,
            "actor_user_id":actor_user_id,
        }
        try:
            if self.service.delete_import(datos):
                return {
                    "success":True,
                    "message": "La importación fue eliminada correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo eliminar la importación\nVerifique que corresponda a su negocio."
                }
        except (ValueError, PermissionError) as e:
            return {
                "success":False,
                "message": f"{e}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": "No se pudo completar la eliminación de la Importación."
            }
    def delete_business(self, business_id, user_id):
        datos = {
            "business_id": business_id,
            "user_id": user_id,
            "actor_user_id": user_id,
        }
        try:
            if self.service.delete_business(datos):
                return {
                    "success": True,
                    "message": "El negocio fue eliminado correctamente"
                }
            return {
                "success": False,
                "message": "No se encontró el negocio."
            }
        except (ValueError, PermissionError) as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "No se pudo completar la eliminación del negocio."
            }
    def get_business(self, business_id: int):
        try:
            business = self.service.get_business(business_id)
            if business is None:
                return {
                    "success": False,
                    "message": "No se encontró el negocio.",
                }
            return {
                "success": True,
                "business": business,
                "categories": list(business.categories),
            }
        except Exception:
            return {
                "success": False,
                "message": "No se pudo consultar la información del negocio.",
            }
