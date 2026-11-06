from decimal import Decimal
from datetime import date, datetime

class RecommendationPresenter:
    #*Prepara las recomendaciones financieras para su presentaciónen la interfaz de usuario.
    ICONS = {
        "alta": ":/icons/exclamationMarkRed.svg",
        "oportunidad": ":/icons/star.svg",
        "informativa": ":/icons/exclamationMarkBlue.svg",
    }
    AREAS = {
        "gastos": "Gastos",
        "ventas": "Ventas",
        "ingresos": "Ingresos",
    }
    PRIORITIES = {
        "alta": {
            "text": "Crítico",
            "badge": "prioridad-alta",
        },
        "oportunidad": {
            "text": "Oportunidad",
            "badge": "oportunidad",
        },
        "informativa": {
            "text": "Informativa",
            "badge": "informativa",
        },
    }
    ACTIONS = {
        "G-01": (
            "Revisa los gastos de esta categoría y compara "
            "los precios de tus proveedores para identificar "
            "posibles oportunidades de ahorro."
        ),
        "G-02": (
            "Analiza los gastos actuales, identifica los "
            "gastos no esenciales y establece prioridades "
            "para mejorar el equilibrio financiero."
        ),
        "V-01": (
            "Identifica los productos cuyas ventas han "
            "disminuido y analiza posibles causas, como "
            "precios, disponibilidad o cambios en la demanda."
        ),
        "V-02": (
            "Analiza qué está impulsando el crecimiento "
            "de este producto y evalúa cómo mantener "
            "su evolución favorable."
        ),
        "V-04": (
            "Verifica si la demanda continúa creciendo "
            "y planifica el inventario para evitar "
            "faltantes de este producto."
        ),
        "V-06": (
            "Examina los días con mayores fluctuaciones "
            "y comprueba si existen patrones relacionados "
            "con la demanda o las actividades comerciales."
        ),
        "I-04": (
            "Comprueba si los ingresos corresponden a "
            "pagos periódicos y considera su posible "
            "recurrencia al planificar el flujo de caja."
        ),
    }
    def preparar(self, recomendacion: dict) -> dict:
        #*Convierte una recomendación original en un diccionario preparado para construir una tarjeta.
        codigo = recomendacion["rule_code"]
        area = recomendacion["area"].lower()
        prioridad = recomendacion["priority"].lower()
        prioridad_info = self.PRIORITIES.get(prioridad,self.PRIORITIES["informativa"],)
        return {
            **recomendacion,
            "area_text": self.AREAS.get(area, area.title()),
            "priority_text": prioridad_info["text"],
            "priority_badge": prioridad_info["badge"],
            "icon_path": self.ICONS.get(
                prioridad,
                self.ICONS["informativa"],
            ),
            "observed_text": self._obtener_dato_observado(
                codigo,
                recomendacion.get("data", {}),
            ),
            "action_text": self.ACTIONS.get(
                codigo,
                "Revisa los datos del período y evalúa "
                "las medidas que mejor se adapten "
                "a las necesidades de tu negocio.",
            ),
        }
    def preparar_todas(self, recomendaciones: list) -> list:
        #*Prepara una colección de recomendaciones.
        return [
            self.preparar(recomendacion)
            for recomendacion in recomendaciones
        ]

    def _obtener_dato_observado(self,codigo: str,data: dict,) -> str:
        #*Genera el texto del dato observado según la regla.
        formatters = {
            "G-01": self._dato_g01,
            "G-02": self._dato_g02,
            "V-01": self._dato_v01,
            "V-02": self._dato_v02,
            "V-04": self._dato_v04,
            "V-06": self._dato_v06,
            "I-04": self._dato_i04,
        }
        formatter = formatters.get(codigo)
        if formatter is None:
            return "No hay datos adicionales disponibles."
        return formatter(data)

    @staticmethod
    def _numero(valor) -> Decimal:
        #*Convierte números a Decimal evitando operaciones aritméticas innecesarias con float.
        if isinstance(valor, Decimal):
            return valor
        return Decimal(str(valor))

    @classmethod
    def _monto(cls, valor) -> str:
        valor = cls._numero(valor)
        return f"C$ {valor:,.2f}"
    @classmethod
    def _porcentaje(cls, valor, incluir_signo=False) -> str:
        valor = cls._numero(valor)
        if incluir_signo and valor > 0:
            return f"+{valor:,.2f}%"
        return f"{valor:,.2f}%"

    @classmethod
    def _cantidad(cls, valor) -> str:
        valor = cls._numero(valor)
        if valor == valor.to_integral_value():
            return f"{valor:,.0f}"
        return f"{valor:,.2f}"

    @staticmethod
    def _fecha(valor) -> str:
        if isinstance(valor, (date, datetime)):
            return valor.strftime("%d/%m/%Y")
        return str(valor)

    def _dato_g01(self, data: dict) -> str:
        return (
            f'Categoría: \n'
            f'{data["category"]}\n'
            f'Monto actual: \n'
            f'{self._monto(data["current_amount"])}\n'
            f'Variación: \n'
            f'{self._porcentaje(data["variation_percentage"], incluir_signo=True)}'
        )

    def _dato_g02(self, data: dict) -> str:
        return (
            f'Diferencia: \n'
            f'{self._monto(data["difference"])}'
        )

    def _dato_v01(self, data: dict) -> str:
        return (
            f'Ventas actuales: \n'
            f'{self._monto(data["current_sales"])}\n'
            f'Ventas anteriores: \n'
            f'{self._monto(data["previous_sales"])}\n'
            f'Variación: \n'
            f'{self._porcentaje(data["variation_percentage"])}'
        )

    def _dato_v02(self, data: dict) -> str:
        return (
            f'Producto: \n'
            f'{data["product"]}\n'
            f'Monto actual: \n'
            f'{self._monto(data["current_amount"])}\n'
            f'Variación: \n'
            f'{self._porcentaje(data["variation_percentage"], incluir_signo=True)}'
        )

    def _dato_v04(self, data: dict) -> str:
        return (
            f'Producto: \n'
            f'{data["product"]}\n'
            f'Cantidad anterior: \n'
            f'{self._cantidad(data["previous_quantity"])}\n'
            f'Cantidad actual: \n'
            f'{self._cantidad(data["current_quantity"])}'
        )

    def _dato_v06(self, data: dict) -> str:
        return (
            f'Media diaria: \n'
            f'{self._monto(data["daily_mean"])}\n'
            f'Coeficiente de variación: \n'
            f'{self._porcentaje(data["coefficient_variation"])}\n'
            f'Días con ventas: \n'
            f'{data["active_days"]} de {data["total_days"]}'
        )

    def _dato_i04(self, data: dict) -> str:
        return (
            f'Categoría: \n'
            f'{data["category"]}\n'
            f'Ocurrencias: \n'
            f'{data["occurrences"]}\n'
            f'Importe mediano: \n'
            f'{self._monto(data["median_amount"])}\n'
            f'Intervalo promedio: \n'
            f'{self._cantidad(data["average_interval_days"])} días'
        )