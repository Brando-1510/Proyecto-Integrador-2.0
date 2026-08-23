from datetime import datetime, timedelta, timezone
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from PySide6.QtCore import QThread, Signal, QFile, QIODevice
from app.config.settings import EMAIL, PASSWORD

#!ESTO AUN NO ESTA TERMINADO


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
    exito_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, email_destino, codigo):
        super().__init__()
        self.email_destino = email_destino
        self.codigo = codigo

    def run(self):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        remitente = EMAIL
        password = PASSWORD

        mensaje = MIMEMultipart("related")
        mensaje["From"] = remitente
        mensaje["To"] = self.email_destino
        mensaje["Subject"] = "Código de recuperación de contraseña - FINANCE"

        #Generar un Content-ID único para la imagen
        logo_cid = make_msgid()

        #Cuerpo del mensaje en formato HTML
        cuerpo_html = f"""
        <html>
            <body style="font-family:Manrope, Arial, sans-serif; color: #0E042F; line-height: 1.6; max-width: 450px; margin: 0 auto; padding: 20px; border: 1px solid #eeeeee; border-radius: 8px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <!-- Usamos el Content-ID quitando los corchetes angulares [1:-1] -->
                    <img src="cid:{logo_cid[1:-1]}" alt="Logo FINANCE" style="width: 130px; height: auto;">
                </div>

                <h3 style="color: #0E042F; margin-top: 0; text-align: center;">Recuperación de Contraseña</h3>
                <p>Te saludamos desde <strong>FINANCE</strong>,</p>
                <p>Has solicitado recuperar tu contraseña. Tu código de verificación es:</p>

                <div style="text-align: center; margin: 25px 0;">
                    <span style="background-color: #f0f4f8; border: 2px dashed #2B21BB; color: #1a365d; font-size: 24px; font-weight: bold; padding: 10px 20px; letter-spacing: 2px; border-radius: 4px;">
                        {self.codigo}
                    </span>
                </div>

                <p style="font-size: 13px; color: #252525; background-color: #fffaf0; border-left: 4px solid #6C6686; padding: 10px; margin-top: 20px;">
                    Este código expirará en <strong>15 minutos</strong>.
                </p>

                <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 20px 0;">
                <p style="font-size: 11px; color: #6C6686; text-align: center; margin: 0;">
                    Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
                </p>
            </body>
        </html>
        """

        #Adjuntamos el texto en su versión HTML
        mensaje.attach(MIMEText(cuerpo_html, "html"))

        #Leer la imagen desde los recursos compilados de Qt (.qrc)
        file = QFile(":/images/logo.png")
        if file.open(QIODevice.ReadOnly):
            img_data = file.readAll().data()
            file.close()

            # Creamos el objeto de imagen adjunta
            imagen_adjunta = MIMEImage(img_data)
            imagen_adjunta.add_header("Content-ID", logo_cid)
            imagen_adjunta.add_header("Content-Disposition", "inline", filename="logo.png")
            mensaje.attach(imagen_adjunta)
        else:
            print("Aviso: No se pudo cargar el logo desde el recurso QRC.")

        #Proceso de envío SMTP tradicional
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(remitente, password)
                server.sendmail(
                    remitente,
                    self.email_destino,
                    mensaje.as_string()
                )
            # Emitimos señal de éxito
            self.exito_signal.emit(self.codigo)
        except Exception as e:
            # Emitimos señal de error con el detalle
            print(f"Error al enviar correo: {e}")
            self.error_signal.emit("No se pudo enviar el correo. Inténtalo nuevamente.")