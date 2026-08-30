class RecoveryController:
    def __init__(self, service):
        self.service = service
    def request_recovery(self, email):
        try:
            datos_codigo = self.service.request_recovery(email)
            return {
                "success": True,
                "message": "Si el correo está registrado, recibirás un código.",
                "datos_codigo": datos_codigo
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "Ocurrió un error al procesar la solicitud."
            }

    def verify_recovery_code(self, user_id, code):
        try:
            recovery = self.service.verify_recovery_code(user_id,code)
            return {
                "success": True,
                "recovery": recovery,
                "message": "El código es válido."
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception:
            return {
                "success": False,
                "message": "Ocurrió un error al verificar el código."
            }

    def change_password(self, recovery, new_password):
        try:
            if self.service.reset_password(recovery, new_password):
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
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": "Ocurrió un error al cambiar la contraseña."
            }