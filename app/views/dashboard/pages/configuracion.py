import os
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QListWidgetItem,QSizePolicy,QMessageBox,
                            QLabel,QInputDialog,QTableWidget,QHeaderView)
from PySide6.QtGui import QFontDatabase,QIntValidator
from PySide6.QtUiTools import QUiLoader
from app.utils.validators import ValidadoresUI
from app.generated import resources_rc
from app.utils.utilsUI import llenar_datos_usuarios
from app.views.estilosTipografia import estilos_fuentes
from PySide6.QtCore import Qt,Signal
from app.models.business import TypeOfBusiness
from app.controllers.configuration_controller import ConfigurationController
from app.views.dashboard.table_models.table_widgets import populate_table

class Configuracion(QWidget):
    choose_business_requested=Signal(object)
    def __init__(self, userBusiness,controller:ConfigurationController):
        super().__init__()
        self.user = userBusiness.user
        self.business = userBusiness.business
        self.userBusiness = userBusiness
        self.categories=userBusiness.business.categories
        self.controller=controller
        #*OBTENER DIRECTORIO ACTUAL
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        #*CARGAR ARCHIVO .UI
        ruta_ui = os.path.normpath(os.path.join(
            directorio_actual,"../../../ui/dashboard/pages/configuracion.ui"))
        loader = QUiLoader()
        self.ui = loader.load(ruta_ui, self)
        if not self.ui:
            print(f"Error crítico: No se pudo cargar el archivo UI en:\n"f"{ruta_ui}")
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        #*Cambios en el ui
        for tabla in (
            self.ui.verEmpleados,self.ui.verUsuarios,self.ui.empleados
        ):
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #Tabwidget
        self.ui.tabWidgetDos.setTabBarAutoHide(False)
        self.ui.tabWidgetDos.tabBar().setExpanding(True)
        self.ui.tabWidgetDos.setDocumentMode(True)
        self.ui.tabWidgetDos.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._cargar_fuentes()
        self.informacion_negocio()
        self.empleados_tab()
        self.operaciones_criticas_tab()
    def _cargar_fuentes(self):
        id_manrope = QFontDatabase.addApplicationFont(":/fonts/Manrope-Regular.ttf")
        id_source = QFontDatabase.addApplicationFont(":/fonts/SourceSans3-Regular.ttf")
        familias_manrope = QFontDatabase.applicationFontFamilies(id_manrope)
        familias_source = QFontDatabase.applicationFontFamilies(id_source)
        if familias_manrope and familias_source:
            estilos = estilos_fuentes(familias_source[0],familias_manrope[0],)
            self.ui.setStyleSheet(self.ui.styleSheet() + estilos)
    def _actualizar_label(self,texto,lbl:QLabel):
        lbl.setText(texto)
    def _actualizar_label_table(
        self,lblNombre:QLabel,lblCorreo:QLabel,table: QTableWidget,lblRol:QLabel | None=None
    ):
        fila = table.currentRow()
        if fila < 0:
            lblNombre.clear()
            lblCorreo.clear()
            if lblRol:
                lblRol.clear()
            return
        nombre = table.item(fila, 0)
        correo = table.item(fila, 1)
        rol = table.item(fila, 2) if lblRol else None
        lblNombre.setText(nombre.text() if nombre else "")
        lblCorreo.setText(correo.text() if correo else "")
        if lblRol:
            lblRol.setText(rol.text() if rol else "")

    #TODOS los metodos relacionadas a la tab de Informacion del negocio
    def informacion_negocio(self):
        #*Cambios en la interfaz:
        self._desabilitar_campos()
        self._datos_defecto_informacion()

        #*Conectar las acciones
        self.ui.agregarCategoria.clicked.connect(self._añadir_categoria)
        self.ui.quitarCategoria.clicked.connect(self._eliminar_categoria)

        self.ui.habilitarEdicion.clicked.connect(self._habilitar_campos)
        self.ui.guardarCambios.clicked.connect(self.guardar_cambios_informacion)
        self.ui.cancelarCambios.clicked.connect(self.cancelar_cambios_informacion)
    def _datos_listwidget(self):
        todos_los_datos=[]
        for i in range(self.ui.listaCategorias.count()):
            item=self.ui.listaCategorias.item(i)
            todos_los_datos.append(item.text())
        return todos_los_datos
    #*Guardar una copia de los valores originales
    def _datos_defecto_informacion(self):
        self.datos_originales = {
            "nombreNegocio": self.business.business_name,
            "descripcionNegocio": self.business.description or "",
            "tipoNegocio": self.business.type_of_business,
            "categorias": {
                category.name
                for category in self.categories
            }
        }
        self.ui.nombreNegocio.setText(self.datos_originales["nombreNegocio"])
        self.ui.descripcion.setPlainText(self.datos_originales["descripcionNegocio"])
        for business_type in TypeOfBusiness:
            self.ui.tipoNegocio.addItem(
                business_type.value,business_type
            )
        index = self.ui.tipoNegocio.findData(self.datos_originales["tipoNegocio"])
        if index != -1:
            self.ui.tipoNegocio.setCurrentIndex(index)
        for category in self.categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.ui.listaCategorias.addItem(item)
    #*Obtener la informacion para mandar al controller
    def _obtener_cambios_informacion(self):
        cambios = {}
        # Nombre
        nombre = self.ui.nombreNegocio.text().strip()
        if nombre != self.datos_originales["nombreNegocio"]:
            cambios["business_name"] = nombre
        # Descripción
        descripcion = self.ui.descripcion.toPlainText().strip()
        if descripcion != self.datos_originales["descripcionNegocio"]:
            cambios["description"] = descripcion
        # Tipo de negocio
        tipo = self.ui.tipoNegocio.currentData()
        if tipo != self.datos_originales["tipoNegocio"]:
            cambios["type_of_business"] = tipo
        # Categorías actuales
        categorias_actuales = {
            self.ui.listaCategorias.item(i).text()
            for i in range(self.ui.listaCategorias.count())
        }
        categorias_originales = self.datos_originales["categorias"]
        # Categorías agregadas
        categorias_agregadas = (categorias_actuales - categorias_originales)
        if categorias_agregadas:
            cambios["categories_to_add"] = sorted(categorias_agregadas)
        # IDs de las categorías eliminadas
        categorias_eliminadas = [
            category.category_id
            for category in self.categories
            if category.name not in categorias_actuales
        ]
        if categorias_eliminadas:
            cambios["categories_to_delete"] = categorias_eliminadas
        return cambios
    #*Estado con el que viene la ui, con los campos desabilitados
    def _desabilitar_campos(self):
        for widget in (
            self.ui.nombreNegocio,self.ui.descripcion,self.ui.tipoNegocio,self.ui.quitarCategoria,
            self.ui.agregarCategoria,self.ui.cancelarCambios,self.ui.guardarCambios
        ):
            widget.setEnabled(False)
    #*Cuando el usuario lo decida, se habilitan los campos
    def _habilitar_campos(self):
        respuesta=QMessageBox.question(
            self,"Habilitar Modo de Edición",
            "Todos los cambios que se generen en esta\nventana afectaran a su negocio\n¿Desea Continuar?"
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            for widget in (
                self.ui.nombreNegocio,self.ui.descripcion,self.ui.tipoNegocio,self.ui.quitarCategoria,
                self.ui.agregarCategoria,self.ui.cancelarCambios,self.ui.guardarCambios
            ):
                widget.setEnabled(True)
        else: return
    #*añadir categoria al listwidget
    def _añadir_categoria(self):
        categoria, ok = QInputDialog.getText(
            self,"Añadir nueva categoría","Introduce el nombre de la categoría"
        )
        if not ok or not categoria.strip():
            return
        categoria = categoria.strip().title()
        elementos = {
            self.ui.listaCategorias.item(i).text().casefold()
            for i in range(self.ui.listaCategorias.count())
        }
        if categoria.casefold() in elementos:
            QMessageBox.warning(
                self,"La categoría ya existe","La categoría que intenta agregar ya está en la lista."
            )
            return
        self.ui.listaCategorias.addItem(categoria)
    #!eliminar categoria
    def _eliminar_categoria(self):
        elemento_actual=self.ui.listaCategorias.currentItem()
        if elemento_actual:
            fila=self.ui.listaCategorias.row(elemento_actual)
            self.ui.listaCategorias.takeItem(fila)
    #*Metodos guardar cambios
    def guardar_cambios_informacion(self):
        cambios = self._obtener_cambios_informacion()
        if not cambios:
            QMessageBox.information(self,"Sin cambios","No se han realizado modificaciones.")
            return
        resultado = self.controller.save_business_changes(
            business_id=self.business.business_id,
            business_name=cambios.get("business_name"),
            type_of_business=cambios.get("type_of_business"),
            description=cambios.get("description"),
            categories_to_add=cambios.get("categories_to_add", []),
            categories_to_delete=cambios.get("categories_to_delete", []),
        )
        if resultado["success"]:
            self.business = resultado["business"]
            self.categories = list(self.business.categories)
            QMessageBox.information(self,"Cambios guardados",resultado["message"])
            # Actualizar la referencia del negocio
            self.business = resultado["business"]
            self._recargar_datos_informacion()
            self._desabilitar_campos()
        else:
            QMessageBox.warning(self,"Error al guardar",resultado["message"])

    #! Metodo para cuando el usuario cancela
    def cancelar_cambios_informacion(self):
        respuesta = QMessageBox.question(
            self,"Cancelar cambios","¿Desea descartar todos los cambios realizados?"
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        self.ui.nombreNegocio.setText(self.datos_originales["nombreNegocio"])
        self.ui.descripcion.setPlainText(self.datos_originales["descripcionNegocio"])
        index = self.ui.tipoNegocio.findData(self.datos_originales["tipoNegocio"])
        self.ui.tipoNegocio.setCurrentIndex(index)
        self.ui.listaCategorias.clear()
        for category in self.categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.ui.listaCategorias.addItem(item)
        self._desabilitar_campos()

    #TODOS los métodos relacionados a la tab de Empleados
    def empleados_tab(self):
        self.ver_empleados_tab()
        self.agregar_empleado_tab()
        self.eliminar_empleado_tab()
    #*Función que maneja esa tab
    def ver_empleados_tab(self):
        self.ui.buscarEmpleado.textChanged.connect(
            lambda: self._ver_empleados(self.ui.buscarEmpleado,self.ui.verEmpleados)
        )
    #*Función que maneja esa tab
    def agregar_empleado_tab(self):
        self.ui.verUsuarios.itemSelectionChanged.connect(lambda: self._actualizar_label_table(
        self.ui.usuario,self.ui.lblCorreo,self.ui.verUsuarios
        ))
        self.ui.rol.currentTextChanged.connect(
            lambda texto:self._actualizar_label(texto,self.ui.lblRol)
        )
        #*Conectar acciones
        self.ui.confirmarEmpleado.clicked.connect(self.agregar_empleado)
        self.ui.buscarEmpleadoAgregar.textChanged.connect(self._ver_usuarios)
    def agregar_empleado(self):
        if self.ui.lblCorreo.text().strip()=="":
            QMessageBox.warning(self,"Acción Inválida","Debe seleccionar un usuario de la tabla")
            return
        resultado=self.controller.link_user(
            self.business.business_id,self.ui.lblCorreo.text(),self.ui.lblRol.text()
        )
        if resultado["success"]:
            QMessageBox.information(self,"Éxito",resultado["message"])
            return
        QMessageBox.warning(self,"No se pudo realizar la acción",resultado["message"])
    #*Ver usuarios
    def _ver_usuarios(self):
        usuarios=self.controller.get_users(self.ui.buscarEmpleadoAgregar.text().strip())
        populate_table(self.ui.verUsuarios,usuarios["usuarios"])
    #*Función que maneja esa tab
    def eliminar_empleado_tab(self):
        self.ui.empleados.itemSelectionChanged.connect(lambda: self._actualizar_label_table(
        self.ui.usuarioSeleccionado,self.ui.correo,self.ui.empleados,self.ui.rolSeleccionado
        ))
        #*Conectar las acciones
        self.ui.btnEliminarEmpleado.clicked.connect(self.eliminar_empleado)
        self.ui.buscarEmpleadoEliminar.textChanged.connect(
            lambda: self._ver_empleados(self.ui.buscarEmpleadoEliminar,self.ui.empleados)
        )
    #*ver empleados
    def _ver_empleados(self,lbl,tabla):
        empleados=self.controller.get_employees(
            lbl.text().strip(),self.business.business_id
        )
        populate_table(tabla,empleados["empleados"])
    #
    def eliminar_empleado(self):
        if self.ui.correo.text().strip()=="" or self.ui.rolSeleccionado.text().strip()=="":
            QMessageBox.warning(self,"Acción Inválida","Debe seleccionar un usuario de la tabla")
            return
        resultado=self.controller.unlink_user(
            self.business.business_id,self.ui.correo.text()
        )
        if resultado["success"]:
            QMessageBox.information(self,"Éxito",resultado["message"])
            return
        QMessageBox.warning(self,"No se pudo realizar la acción",resultado["message"])

    #TODOS los metodos relacionados a la tab de operaciones criticas
    def operaciones_criticas_tab(self):
        self._configurar_lineEdit()
        self.ui.eliminarImportacion.clicked.connect(self.eliminar_importacion)
        self.ui.eliminarNegocio.clicked.connect(self.eliminar_negocio)

    def _configurar_lineEdit(self):
        validador=QIntValidator(self)
        self.ui.idImportacion.setValidator(validador)
    def eliminar_importacion(self):
        if not ValidadoresUI.tienen_contenido(self.ui.idImportacion):
            QMessageBox.warning(self,"Error","Debe ingresar un id de importación para\nrealizar esta operación")
            return
        respuesta = QMessageBox.question(
            self,"Confirmación","¿Deseas eliminar la importación?\nEsta operación no puede revertirse",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            importacion=int(self.ui.idImportacion.text())
            resultado=self.controller.delete_import(self.business.business_id,importacion)
            if resultado["success"]:
                QMessageBox.information(self,"Éxito",resultado["message"])
                return
            QMessageBox.warning(self,"Error",resultado["message"])
    def eliminar_negocio(self):
        respuesta = QMessageBox.question(
            self,"Confirmación","¿Deseas eliminar el Negocio?\nEsta operación no puede revertirse",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            resultado=self.controller.delete_business(
                self.business.business_id,self.user.user_id
            )
            if resultado["success"]:
                QMessageBox.information(self,"Éxito",resultado["message"])
                self.choose_business_requested.emit(self.user)
                return
            QMessageBox.warning(self,"Error",resultado["message"])