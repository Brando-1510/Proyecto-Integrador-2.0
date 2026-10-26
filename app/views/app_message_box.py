from PySide6.QtWidgets import QMessageBox,QWidget,QPushButton


class AppMessageBox:
    COLOR_PRINCIPAL = "#5D38BB"
    COLOR_HOVER = "#744BCC"
    COLOR_PRESSED = "#472A8F"
    COLOR_TEXTO = "#F7F7F7"
    BOTON_ANCHO = 100
    BOTON_ALTO = 30

    def __init__(self,source_family: str,parent: QWidget | None = None,):
        self.parent = parent
        self.source_family = source_family

    def _crear_mensaje(
        self,titulo: str,texto: str,icono: QMessageBox.Icon,botones: QMessageBox.StandardButton,
    ) -> QMessageBox:
        msg = QMessageBox(self.parent)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(icono)
        msg.setStandardButtons(botones)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: #F7F7F7;
            }}
            QMessageBox QLabel {{
                font-family: "{self.source_family}";
                font-size: 13px;
                font-weight: 600;
                color: #172554;
            }}
            QMessageBox QPushButton {{
                font-family: "{self.source_family}";
                font-size: 12px;
                font-weight: bold;
                color: {self.COLOR_TEXTO};
                background-color: {self.COLOR_PRINCIPAL};
                border: none;
                border-radius: 5px;
                padding: 0px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {self.COLOR_HOVER};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {self.COLOR_PRESSED};
            }}
        """)
        # Fijar las dimensiones después de crear los botones.
        for boton in msg.buttons():
            if isinstance(boton, QPushButton):
                boton.setFixedSize(
                    self.BOTON_ANCHO,
                    self.BOTON_ALTO,
                )
        return msg

    def error(self, titulo: str, texto: str) -> None:
        msg = self._crear_mensaje(
            titulo,
            texto,
            QMessageBox.Icon.Critical,
            QMessageBox.StandardButton.Ok,
        )
        msg.exec()
    def advertencia(self, titulo: str, texto: str) -> None:
        msg = self._crear_mensaje(
            titulo,texto,QMessageBox.Icon.Warning,QMessageBox.StandardButton.Ok,
        )
        msg.exec()

    def informacion(self, titulo: str, texto: str) -> None:
        msg = self._crear_mensaje(
            titulo,
            texto,
            QMessageBox.Icon.Information,
            QMessageBox.StandardButton.Ok,
        )
        msg.exec()
    def confirmar(self,titulo: str,texto: str,) -> bool:
        msg = self._crear_mensaje(
            titulo,
            texto,
            QMessageBox.Icon.Question,
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
        )
        respuesta = msg.exec()
        return respuesta == QMessageBox.StandardButton.Yes
