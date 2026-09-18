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