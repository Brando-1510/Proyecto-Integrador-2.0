from PySide6.QtGui import QGuiApplication

def obtener_geometria_pantalla():
    #Obtiene el área disponible de la pantalla principal.
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return None
    return screen.availableGeometry()

def obtener_tamano_pantalla():
    #Devuelve el ancho y alto disponibles de la pantalla.
    geometry = obtener_geometria_pantalla()
    if geometry is None:
        return 0, 0
    return geometry.width(), geometry.height()


def calcular_tamano_pantalla(porcentaje_ancho, porcentaje_alto):
    #Calcula un tamaño proporcional al tamaño de la pantalla.
    ancho, alto = obtener_tamano_pantalla()
    return (int(ancho * porcentaje_ancho),int(alto * porcentaje_alto))