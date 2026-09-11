from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

class TarjetaNegocio(QFrame):
    seleccionada = Signal(object)
    def __init__(self, negocio, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.negocio = negocio
        self.esta_seleccionada=False
        # Propiedad establecida en Designer
        self.setProperty("tarjeta", "Negocio")
        self.crear_ui()
        self.style().unpolish(self)
        self.style().polish(self)
    def crear_ui(self):
        # Layout principal
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 15, 20, 15)
        layout_principal.setSpacing(20)
        # Icono
        self.lblIcono = QLabel()
        self.lblIcono.setFixedSize(60, 60)
        self.lblIcono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(self.obtener_icono())
        pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lblIcono.setPixmap(pixmap)
        layout_info = QVBoxLayout()
        layout_info.setSpacing(5)
        # Nombre del negocio
        self.lblNombre = QLabel(self.negocio.business.business_name)
        self.lblNombre.setObjectName("nombreNegocio")
        self.lblNombre.setProperty("texto", "Destacado")
        # Rol del usuario
        self.lblRol = QLabel(self.negocio.role.value)
        self.lblRol.setObjectName("rolNegocio")
        self.lblRol.setProperty("texto", "Descripcion")
        for label in [self.lblNombre, self.lblRol]:
            label.ensurePolished()
            label.style().unpolish(label)
            label.style().polish(label)
        # Agregar elementos al layout vertical de información
        layout_info.addWidget(self.lblNombre)
        layout_info.addWidget(self.lblRol)

        # Armar tarjeta insertando componentes al layout principal
        layout_principal.addWidget(self.lblIcono)
        layout_principal.addLayout(layout_info)


    def obtener_icono(self):
        iconos = {
            "Barberia": ":/images/businessIcons/barberShop.png",
            "Tienda de Ropa": ":/images/businessIcons/clotheStore.png",
            "Cafetería": ":/images/businessIcons/coffeShop.png",
            "Farmacia": ":/images/businessIcons/drugStore.png",
            "Restaurante": ":/images/businessIcons/restaurant.png",
            "Ferretería": ":/images/businessIcons/hardwareStore.png",
            "Pulperia": ":/images/businessIcons/shop.png",
            "Otro": ":/images/businessIcons/shop.png"
        }
        return iconos.get(
            self.negocio.business.type_of_business.value,
            ":/icons/default.png"
        )
    def mousePressEvent(self, event):
        self.seleccionada.emit(self.negocio)
        super().mousePressEvent(event)