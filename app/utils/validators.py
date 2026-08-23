from PySide6.QtWidgets import QLabel, QComboBox, QLineEdit, QTextEdit
import re
class ValidadoresUI:
    @staticmethod
    #*Valida que un elemento tenga texto o sea valido
    def tienen_contenido(*widgets) -> bool:
        #*Devuelve True solo si todos los widgets pasados tienen datos válidos
        for widget in widgets:
            #Los QComboBox lo validamos por índice
            if isinstance(widget, QComboBox):
                if widget.currentIndex() <= 0:
                    return False
            # Para QLineEdit y QLabel
            elif hasattr(widget, 'text'):
                if not bool(widget.text().strip()):
                    return False
            # Para QTextEdit
            elif hasattr(widget, 'toPlainText'):
                if not bool(widget.toPlainText().strip()):
                    return False
        return True

class ValidadoresDatos:
    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    @classmethod
    def validar_correo(cls,correo: str) -> bool:
        correo = correo.strip()
        if not correo:
            return False
        return bool(re.fullmatch(cls.EMAIL_PATTERN, correo))
