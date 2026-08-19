import os
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QFontDatabase
from PySide6.QtUiTools import QUiLoader

class VentanaCrearCuenta(QWidget):
    def __init__(self):
        super().__init__()
        #*CARGAR ARCHIVO .UI
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(directorio_actual,"../../ui/createAccount.ui")
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en: {ruta_ui}")
            return
        #*CARGAR TIPOGRAFÍAS
        # Manrope
        font_id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        # Source Sans 3
        font_id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        if font_id_manrope == -1:
            print("Advertencia: No se pudo cargar Manrope.")
        if font_id_source == -1:
            print("Advertencia: No se pudo cargar Source Sans 3.")
        # Obtener las familias reales registradas
        manrope_family = None
        source_family = None
        if font_id_manrope != -1:
            manrope_family = QFontDatabase.applicationFontFamilies(font_id_manrope)[0]
        if font_id_source != -1:
            source_family = QFontDatabase.applicationFontFamilies(font_id_source)[0]

        #*APLICAR TIPOGRAFÍAS
        if manrope_family and source_family:
            self.ui.setStyleSheet(f"""
                /*FUENTE GENERAL*/
                QWidget {{
                    font-family: '{source_family}';
                    font-size: 14px;
                }}

                /*TÍTULOS PRINCIPALES*/

                QLabel[styleClass="tituloPrincipal"] {{
                    font-family: '{manrope_family}';
                    font-weight: 700;
                }}
                /*TÍTULOS DE SECCIÓN*/
                QLabel[styleClass="tituloSeccion"] {{
                    font-family: '{manrope_family}';
                    font-weight: 600;
                }}
                /*TEXTO GENERAL*/
                QLabel[styleClass="textoPaso"] {{
                    font-family: '{source_family}';
                    font-weight: 400;
                }}
            """)
        else:
            print("Advertencia: No se pudieron cargar correctamente las fuentes")

        self.showMaximized()
