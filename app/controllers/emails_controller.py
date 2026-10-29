from app.services.user_business_service import UserBusinessService
from app.workers.email_sender_worker import EnviarCorreoThread
class EmailController:
    def __init__(self,service:UserBusinessService):
        self.service=service
    def get_data(self,business_id:int,user_id:int):
        try:
            resultado=self.service.get_employees(business_id,user_id)
            return {
                "success":True,
                "resultado":resultado
            }
        except Exception as e:
            print(f"ERROR DETECTADO: {e}")
            return{
                "success":False,
                "message": "No se pudieron cargar los usuarios vinculados\na este negocio."
            }
    def enviar_email(self, datos, on_success, on_error) -> None:
        hilo = EnviarCorreoThread(
            email_destino=datos["destinatario"],asunto=datos["asunto"],
            cuerpo=datos["cuerpo"],remitente_nombre=datos["remitente"],remitente_email=datos["remitente_correo"],
        )
        hilo.exito_signal.connect(on_success)
        hilo.error_signal.connect(on_error)
        self.email_thread = hilo
        hilo.start()