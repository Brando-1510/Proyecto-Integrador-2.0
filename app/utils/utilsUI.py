from PySide6.QtWidgets import QTableWidgetItem
def obtener_icono(negocio):
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
    return iconos.get(negocio.business.type_of_business.value,":/icons/default.png")
def llenar_datos_usuarios(tabla, user_businesses):
    tabla.setRowCount(0)
    for user_business in user_businesses:
        user = user_business.user
        row = tabla.rowCount()
        tabla.insertRow(row)
        tabla.setItem(row, 0, QTableWidgetItem(user.username))
        tabla.setItem(row, 1, QTableWidgetItem(user.email))
        tabla.setItem(row, 2, QTableWidgetItem(user_business.role.value))
        tabla.setItem(
            row, 3,
            QTableWidgetItem(
                user_business.created_at.strftime("%d/%m/%Y")
            )
        )