from PySide6.QtWidgets import QLabel, QComboBox, QLineEdit, QTextEdit,QMessageBox
from PySide6 import QtCore
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
    @staticmethod
    def comparar_contraseñas(ventana,password,password_confirmar):
        if password != password_confirmar:
            QMessageBox.critical(ventana,"Error","Las Contraseñas deben de coincidir")
            return
    @staticmethod
    def validar_fecha(ventana,fecha):
        if not fecha.isValid():
            QMessageBox.critical(ventana,"Error","La fecha ingresada no es válida")
            return
        py_fecha=fecha.toPython()
        hoy = QtCore.QDate.currentDate().toPython()
        if py_fecha > hoy:
            QMessageBox.critical(ventana,"Error","No se permite seleccionar una fecha futura")
            return
    @staticmethod
    def evaluar_contrasena(texto,ventana):
        # Reglas de validación
        largo = len(texto) >= 8
        mayuscula = bool(re.search(r"[A-Z]", texto))
        minuscula = bool(re.search(r"[a-z]", texto))
        numero = bool(re.search(r"[0-9]", texto))
        especial = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-=\[\]\\/;`~]", texto))
        # Comprobar si cumple con absolutamente todo
        if largo and mayuscula and minuscula and numero and especial:
            return True
        else:
            QMessageBox.warning(ventana,"Problema con la Contraseña","Contraseña débil (revisa los requisitos)")
            return