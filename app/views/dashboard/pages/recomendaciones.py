import os
from PySide6.QtWidgets import (
    QWidget,QVBoxLayout,QMessageBox,QFrame,QSizePolicy,QHBoxLayout,QLabel,QPushButton,
)
from PySide6.QtGui import QFontDatabase, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from app.generated import resources_rc
from app.views.estilosTipografia import estilos_fuentes
from app.utils.recommendation_presenter import RecommendationPresenter

class Recomendaciones(QWidget):
    def __init__(self, userBusiness, controller=None):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.controller = controller
        # Estado de las recomendaciones de esta página.
        self.recommendations = []
        self.dismissed_ids = set()
        self.tarjetas_por_area = {
            "todas": [],
            "ventas": [],
            "gastos": [],
            "ingresos": [],
        }
        self.presenter = RecommendationPresenter()
        # Cargar interfaz de Qt Designer.
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.normpath(
            os.path.join(
                directorio_actual,
                "../../../ui/dashboard/pages/recomendaciones.ui",
            )
        )
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            raise RuntimeError(f"No se pudo cargar la interfaz:\n{ruta_ui}")
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addWidget(self.ui)
        self._cargar_fuentes()
        self._configurar_pestanas()
        self.ocultar_label()
        self.actualizar_interfaz()
        self.ui.periodo.currentTextChanged.connect(self.actualizar_interfaz)

    #*Configuración inicial
    def _cargar_fuentes(self):
        id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        familias_manrope = QFontDatabase.applicationFontFamilies(id_manrope)
        familias_source = QFontDatabase.applicationFontFamilies(id_source)
        if familias_manrope and familias_source:
            estilos = estilos_fuentes(familias_source[0],familias_manrope[0],)
            self.ui.setStyleSheet(self.ui.styleSheet() + estilos)
    def _configurar_pestanas(self):
        self.pestanas = {
            "todas": self.ui.TodasTab,
            "ventas": self.ui.VentasTab,
            "gastos": self.ui.GastosTab,
            "ingresos": self.ui.IngresosTab,
        }
        self.layouts_recomendaciones = {
            area: pestana.layout()
            for area, pestana in self.pestanas.items()
        }
        # Etiquetas que se muestran cuando no hay tarjetas.
        self.labels_vacios = {
            "todas": self.ui.lblTodas,
            "ventas": self.ui.lblVentas,
            "gastos": self.ui.lblGasto,
            "ingresos": self.ui.lblIngreso,
        }
        for area, layout in self.layouts_recomendaciones.items():
            if layout is None:
                raise RuntimeError(f"La pestaña '{area}' no tiene un layout.")
    #*Obtención de datos
    def actualizar_interfaz(self):
        datos = self.recolectar_datos()
        try:
            resultado = self.controller.get_recommendations(datos)
        except Exception as error:
            QMessageBox.warning(self.ui,"Error al cargar datos",str(error),)
            return
        if not resultado.get("success", False):
            QMessageBox.warning(self.ui,"Error al cargar datos",
                resultado.get("message","No fue posible obtener las recomendaciones.",),
            )
            return
        recomendaciones = resultado.get("recommendations", [])
        self.mostrar_recomendaciones(recomendaciones)

    def recolectar_datos(self):
        return {
            "business_id": self.business.business_id,
            "rol": self.userBusiness.role,
            "periodo": self.ui.periodo.currentText(),
        }

    #*Mostrar y actualizar recomendaciones
    def mostrar_recomendaciones(self, recomendaciones):
        self._limpiar_tarjetas()
        self.recommendations = self.presenter.preparar_todas(recomendaciones)
        self.actualizar_contadores(self.recommendations)
        for indice, recomendacion in enumerate(self.recommendations):
            # Identificador de la recomendación dentro de la página.
            recomendacion["_ui_id"] = self._crear_id(recomendacion,indice,)
            if recomendacion["_ui_id"] in self.dismissed_ids:
                continue
            area = recomendacion.get("area", "").lower()
            # Todas las recomendaciones aparecen en la primera pestaña.
            tarjeta_todas = self._crear_tarjeta(recomendacion)
            self._agregar_tarjeta("todas", tarjeta_todas)
            # En las demás pestañas solo aparece el área correspondiente.
            if area in ("ventas", "gastos", "ingresos"):
                tarjeta_area = self._crear_tarjeta(recomendacion)
                self._agregar_tarjeta(area, tarjeta_area)
        activas = [
        r for r in self.recommendations
        if r.get("_ui_id") not in self.dismissed_ids
        ]
        self.actualizar_contadores(activas)
        self._actualizar_estados_vacios()

    @staticmethod
    def _crear_id(recomendacion, indice):
        # Incluye datos para diferenciar recomendaciones de una misma regla.
        return (
            recomendacion.get("rule_code", ""),
            recomendacion.get("title", ""),
            repr(recomendacion.get("data", {})),
            indice,
        )

    def _agregar_tarjeta(self, area, tarjeta):
        layout = self.layouts_recomendaciones[area]
        layout.addWidget(tarjeta)
        self.tarjetas_por_area[area].append(tarjeta)

    def _limpiar_tarjetas(self):
        for area, tarjetas in self.tarjetas_por_area.items():
            layout = self.layouts_recomendaciones[area]
            for tarjeta in tarjetas:
                layout.removeWidget(tarjeta)
                tarjeta.deleteLater()
            tarjetas.clear()

    #*Construcción de las tarjetas
    def _crear_tarjeta(self, recomendacion):
        card = QFrame()
        card.setProperty("recommendation_id",recomendacion["_ui_id"],)
        card.setObjectName("cardRecomendacion")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setProperty("carta", "Dashboard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum,)
        principal = QHBoxLayout(card)
        principal.setContentsMargins(20, 18, 20, 18)
        principal.setSpacing(24)
        # Icono de la recomendación.
        layout_icono = QVBoxLayout()
        lbl_icono = QLabel()
        pixmap = QPixmap(recomendacion["icon_path"])
        if not pixmap.isNull():
            lbl_icono.setPixmap(pixmap)
        lbl_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icono.setScaledContents(True)
        lbl_icono.setFixedSize(48, 48)
        layout_icono.addWidget(lbl_icono,alignment=Qt.AlignmentFlag.AlignTop,)
        layout_icono.addStretch()
        # Información principal.
        layout_descripcion = QVBoxLayout()

        lbl_titulo = QLabel(recomendacion.get("title", "Recomendación financiera"))
        lbl_titulo.setProperty("texto", "Destacado")
        lbl_titulo.setWordWrap(True)
        layout_descripcion.addWidget(lbl_titulo)
        layout_badges = QHBoxLayout()
        layout_badges.setSpacing(8)
        lbl_categoria = QLabel(recomendacion["area_text"])
        lbl_categoria.setProperty("badge", "categoria")
        lbl_prioridad = QLabel(recomendacion["priority_text"])
        lbl_prioridad.setProperty("badge",recomendacion["priority_badge"],)
        layout_badges.addWidget(lbl_categoria)
        layout_badges.addWidget(lbl_prioridad)
        layout_badges.addStretch()
        layout_descripcion.addLayout(layout_badges)
        lbl_descripcion = QLabel(recomendacion.get("description","No hay una descripción disponible.",))
        lbl_descripcion.setProperty("texto", "Descripcion")
        lbl_descripcion.setWordWrap(True)
        lbl_dato = QLabel("Dato observado:")
        lbl_dato.setProperty("texto", "Destacado")
        lbl_dato_observado = QLabel(
            recomendacion.get(
                "observed_text",
                "No hay datos adicionales disponibles.",
            )
        )
        lbl_dato_observado.setProperty("texto", "Descripcion")
        lbl_dato_observado.setWordWrap(True)
        layout_descripcion.addWidget(lbl_descripcion)
        layout_descripcion.addWidget(lbl_dato)
        layout_descripcion.addWidget(lbl_dato_observado)
        # Acción sugerida y botón para quitar.
        layout_accion = QVBoxLayout()
        lbl_accion = QLabel("Acción sugerida")
        lbl_accion.setProperty("texto", "Destacado")
        lbl_accion_desc = QLabel(
            recomendacion.get("action_text","Revisa los datos y evalúa las medidas adecuadas.",)
        )
        lbl_accion_desc.setWordWrap(True)
        boton_quitar = QPushButton("Quitar")
        boton_quitar.setProperty("boton", "Secundario")
        boton_quitar.clicked.connect(
            lambda checked=False, rec_id=recomendacion["_ui_id"]:
                self.quitar_recomendacion(rec_id)
        )

        layout_accion.addWidget(lbl_accion)
        layout_accion.addWidget(lbl_accion_desc)
        layout_accion.addStretch()
        layout_accion.addWidget(boton_quitar,alignment=Qt.AlignmentFlag.AlignRight,)
        principal.addLayout(layout_icono)
        principal.addLayout(layout_descripcion, 3)
        principal.addLayout(layout_accion, 2)
        return card

    #*Quitar recomendaciones
    def quitar_recomendacion(self, recomendacion_id):
        self.dismissed_ids.add(recomendacion_id)
        for area, tarjetas in self.tarjetas_por_area.items():
            layout = self.layouts_recomendaciones[area]
            for tarjeta in tarjetas[:]:
                if tarjeta.property("recommendation_id") == recomendacion_id:
                    layout.removeWidget(tarjeta)
                    tarjetas.remove(tarjeta)
                    tarjeta.deleteLater()
        activas = [
        r for r in self.recommendations
        if r.get("_ui_id") not in self.dismissed_ids
        ]
        self.actualizar_contadores(activas)
        self._actualizar_estados_vacios()

    #*Estados vacíos
    def _actualizar_estados_vacios(self):
        for area, label in self.labels_vacios.items():
            hay_tarjetas = bool(self.tarjetas_por_area[area])
            label.setVisible(not hay_tarjetas)
    def ocultar_label(self):
        for label in self.labels_vacios.values():
            label.hide()
    def actualizar_contadores(self, recomendaciones):
        cantidades = {
            "alta": 0,
            "oportunidad": 0,
            "informativa": 0,
        }
        for recomendacion in recomendaciones:
            prioridad = recomendacion.get("priority", "").lower()
            if prioridad in cantidades:
                cantidades[prioridad] += 1
        self.ui.cantidadPrioridad.setText(str(cantidades["alta"]))
        self.ui.cantidadOportunidades.setText(str(cantidades["oportunidad"]))
        self.ui.cantidadInformativas.setText(str(cantidades["informativa"]))

