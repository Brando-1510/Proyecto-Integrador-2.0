#Cálculos financieros reutilizables para los informes.
from decimal import Decimal, ROUND_HALF_UP

class ReportAnalyticsService:
    @staticmethod
    def compare(name: str, current, previous) -> dict:
        """Compara importes monetarios usando Decimal, sin dividir entre cero."""
        current = Decimal(str(current or 0))
        previous = Decimal(str(previous or 0))
        difference = current - previous
        percent = None
        if previous != 0:
            percent = ((difference / abs(previous)) * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return {
            "nombre": name,
            "actual": current,
            "anterior": previous,
            "diferencia": difference,
            "porcentaje": percent,
        }
