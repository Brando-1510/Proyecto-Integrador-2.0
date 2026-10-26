from datetime import date
from app.services.user_services import UserService
class UserController:
    def __init__(self, service:UserService):
        self.service = service
    def register_user(self, name, email, date, password):
        try:
            user = self.service.save_user(
                name,
                email,
                date,
                password
            )
            return {
                "success": True,
                "message": "Usuario registrado correctamente",
                "user": user
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            print("ERROR AL REGISTRAR USUARIO:", repr(e))
            return {
                "success": False,
                "message": "Ocurrió un error al registrar el usuario"
            }
    def login(self,email,password):
        try:
            user=self.service.login_user(email,password)
            return{
                "success": True,
                "message": "Inicio de Sesión Exitoso",
                "user": user
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "Ocurrió un error al iniciar sesión"
            }

    def verify_user(self,email,password):
        try:
            user=self.service.login_user(email,password)
            return{
                "success": True,
                "message": "Usuario confirmado"
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "Ocurrió un error al confirmar al usuario"
            }
    def save_changes(
        self,user_id:int,username:str | None=None,email:str | None=None,
        fecha:date | None=None
    ):
        try:
            return self.service.save_changes(
                user_id=user_id,username=username,email=email,fecha=fecha
            )
        except Exception:
            return {
                "success": False,
                "message": "No se pudo procesar la solicitud.",
            }
    def change_password(self,user_id,password):
        try:
            if self.service.change_password(user_id,password):
                return {
                    "success": True,
                    "message": "La contraseña fue cambiada."
                }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "Ocurrió un error al cambiar la contraseña."
            }