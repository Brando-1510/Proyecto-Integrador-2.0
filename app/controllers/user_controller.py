class UserController:
    def __init__(self, service):
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
        except Exception:
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