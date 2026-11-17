from decimal import Decimal
from app.utils.format_utils import FormatUtils

class ReportInsightsService:
    @staticmethod
    def generate(data: dict) -> list[str]:
        findings: list[str] = []
        income = data.get("ingresos")
        expenses = data.get("gastos")
        sales = data.get("ventas")
        if income is not None and expenses is not None:
            balance = income["total_ingresos"] - expenses["total_gastos"]
            relation = (
                "superaron" if balance > 0 else
                "fueron inferiores a" if balance < 0 else
                "igualaron"
            )
            findings.append(
                f"Los ingresos registrados como movimientos {relation} los gastos "
                f"en el período. Saldo de movimientos: {FormatUtils.format_currency(balance)}."
            )
        for comparison in data.get("comparaciones", []):
            current = comparison["actual"]
            previous = comparison["anterior"]
            difference = comparison["diferencia"]
            if previous == 0:
                if current != 0:
                    findings.append(
                        f"{comparison['nombre']}: no existe una base distinta de cero "
                        "en el período anterior para calcular una variación porcentual."
                    )
                continue
            if difference == 0:
                findings.append(f"{comparison['nombre']}: sin variación frente al período anterior.")
            else:
                direction = "aumentó" if difference > 0 else "disminuyó"
                percent = abs(comparison["porcentaje"])
                findings.append(
                    f"{comparison['nombre']} {direction} {percent:.2f}% "
                    "respecto al período anterior comparable."
                )
        if sales is not None and sales.get("ventas_por_producto"):
            leader = sales["ventas_por_producto"][0]
            findings.append(
                f"Producto o servicio con mayor monto vendido: {leader['nombre']} "
                f"({FormatUtils.format_currency(leader['total'])})."
            )
        for section, label in ((income, "ingresos"), (expenses, "gastos")):
            if section is not None:
                key = f"{label}_por_categoria"
                if section.get(key):
                    category = section[key][0]
                    findings.append(
                        f"Categoría con mayor monto de {label}: {category['nombre']} "
                        f"({FormatUtils.format_currency(category['total'])})."
                    )
        return findings[:6] or [
            "No se registraron datos suficientes para identificar variaciones en este período."
        ]
