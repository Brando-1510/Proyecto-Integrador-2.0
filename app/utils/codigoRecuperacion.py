from datetime import datetime, timedelta,timezone
import secrets
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PySide6.QtCore import QThread, Signal

#*Función para generar el código
def generar_codigo_recuperacion():
    codigo_numerico = str(secrets.randbelow(900000) + 100000)
    token_seguro = secrets.token_hex(32)
    expira_en = datetime.now(timezone.utc) + timedelta(minutes=15)
    return {
        "codigo_numerico": codigo_numerico,
        "token_seguro": token_seguro,
        "expira_en": expira_en
    }

#*Hilo para enviar el email sin congelar la interfaz
class EnviarCorreoThread(QThread):
    # Señales para avisar a la interfaz si tuvo éxito o error
    exito_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, email_destino, codigo):
        super().__init__()
        self.email_destino = email_destino
        self.codigo = codigo

    def run(self):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        remitente = "tu_correo@gmail.com"
        password = "tu_contraseña_de_aplicacion"

        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = self.email_destino
        mensaje["Subject"] = "Código de recuperación de contraseña"

        cuerpo = f"""
        Hola,
        Has solicitado recuperar tu contraseña. 
        Tu código de verificación es: {self.codigo}
        
        Este código expirará en 15 minutos.
        """
        mensaje.attach(MIMEText(cuerpo, "plain"))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(remitente, password)
            server.sendmail(remitente, self.email_destino, mensaje.as_string())
            server.quit()
            
            # Emitimos señal de éxito
            self.exito_signal.emit(self.codigo)
        except Exception as e:
            # Emitimos señal de error con el detalle
            self.error_signal.emit(str(e))