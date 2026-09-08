from PySide6.QtWidgets import (QFrame,QLabel,QHBoxLayout,QVBoxLayout)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class TarjetaNegocio(QFrame):
    def __init__(self, negocio, parent=None):
        super().__init__(parent)
        self.negocio = negocio
        #*Añadiendo la propiedad establecida en el designer
        self.setProperty("tarjeta", "Negocio")
        self.crear_ui()
        #*Refrescar el estilo después de establecer la propiedad
        self.style().unpolish(self)
        self.style().polish(self)
    def crear_ui(self):
        # Layout principal de la tarjeta
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 15, 20, 15)
        layout_principal.setSpacing(20)
        #*Icono
        self.lblIcono = QLabel()
        self.lblIcono.setFixedSize(70, 70)
        self.lblIcono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(self.obtener_icono())
        pixmap = pixmap.scaled(60,60,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.lblIcono.setPixmap(pixmap)
        #*Información
        layout_info = QVBoxLayout()
        layout_info.setSpacing(5)
        # Nombre del negocio
        self.lblNombre = QLabel(self.negocio.business_name)
        self.lblNombre.setObjectName("nombreNegocio")
        # Rol del usuario
        self.lblRol = QLabel(self.negocio.role)
        self.lblRol.setObjectName("rolNegocio")
        layout_info.addWidget(self.lblNombre)
        layout_info.addWidget(self.lblRol)
        layout_info.addStretch()
        #Armar tarjeta
        layout_principal.addWidget(self.lblIcono)
        layout_principal.addLayout(layout_info)
    def obtener_icono(self):
        iconos = {
            "Barbería": ":/images/businessIcons/barberShop.png",
            "Tienda de Ropa": ":/images/businessIcons/clotheStore.png",
            "Cafetería": ":/images/businessIcons/coffeShop.png",
            "Farmacia": ":/images/businessIcons/drugStore.png",
            "Restaurante": ":/images/businessIcons/restaurant.png",
            "Ferreteria": ":/images/businessIcons/hardwareStore.png",
            "Pulperia": ":/images/businessIcons/shop.png",
            "Otro": ":/images/businessIcons/shop.png"
        }
        return iconos.get(self.negocio.type_of_business,":/icons/default.png")