import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.settings import EMAIL, PASSWORD
from PySide6.QtCore import QThread, Signal

class EnviarCorreoThread(QThread):
    exito_signal = Signal()
    error_signal = Signal(str)
    def __init__(self,email_destino: str,asunto: str,cuerpo: str,remitente_nombre: str,remitente_email: str,):
        super().__init__()
        self.email_destino = email_destino
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.remitente_nombre = remitente_nombre
        self.remitente_email = remitente_email
    def run(self):
        try:
            mensaje = MIMEMultipart("alternative")
            mensaje["From"] = EMAIL
            mensaje["To"] = self.email_destino
            mensaje["Subject"] = self.asunto
            cuerpo_html = f"""
            <html>
                <body style="
                    font-family: Arial, sans-serif;
                    color: #0E042F;
                    line-height: 1.6;
                ">
                    <h2>Mensaje de FINANZEN</h2>
                    <p>
                        <strong>De:</strong>
                        {self.remitente_nombre}
                    </p>
                    <p>
                        <strong>Correo:</strong>
                        {self.remitente_email}
                    </p>
                    <hr>
                    <div>
                        {self.cuerpo}
                    </div>
                    <hr>
                    <p style="color: #6C6686; font-size: 12px;">
                        Mensaje enviado desde FINANZEN.
                    </p>
                </body>
            </html>
            """
            mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.sendmail(
                    EMAIL,[self.email_destino],mensaje.as_string(),
                )
            self.exito_signal.emit()
        except Exception:
            self.error_signal.emit(
                "No se pudo enviar el correo. "
                "Verifica la conexión e inténtalo nuevamente."
            )