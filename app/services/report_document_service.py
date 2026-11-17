#Adaptador entre los datos de negocio, Matplotlib y las plantillas Jinja2
from pathlib import Path
from tempfile import TemporaryDirectory
from app.services.report_service import ReportService
from app.pdf_templates.pdf_generator import PdfGenerator
from app.utils.report_charts import ReportCharts
from app.utils.format_utils import FormatUtils

class ReportDocumentService:
    TITLES = {
        "ventas": "Informe de ventas",
        "ingresos": "Informe de ingresos",
        "gastos": "Informe de gastos",
        "general": "Informe financiero general",
    }
    def __init__(self, report_service: ReportService | None = None,
                pdf_generator: PdfGenerator | None = None):
        self.report_service = report_service or ReportService()
        self.pdf_generator = pdf_generator or PdfGenerator()
    def generate(self, request: dict) -> bytes:
        report = self.report_service.get_report_data(request)
        with TemporaryDirectory(prefix="finanzen_report_") as temp:
            template_data = self._prepare(report, Path(temp))
            pdf = self.pdf_generator.generate_report(template_data)
            if not pdf or not pdf.startswith(b"%PDF-"):
                raise RuntimeError("La generación no produjo un documento PDF válido.")
            return pdf
    @staticmethod
    def _prepare(report: dict, temp: Path) -> dict:
        m = report["metadata"]
        result = {
            "tipo_reporte": m["tipo_reporte"],
            "titulo_reporte": ReportDocumentService.TITLES[m["tipo_reporte"]],
            "periodo_inicio": FormatUtils.format_report_date(m["fecha_inicio"]),
            "periodo_fin": FormatUtils.format_report_date(m["fecha_fin"]),
            "periodo_anterior_inicio": FormatUtils.format_report_date(m["periodo_anterior_inicio"]),
            "periodo_anterior_fin": FormatUtils.format_report_date(m["periodo_anterior_fin"]),
            "fecha_generacion": FormatUtils.format_report_date(m["generado_el"].date()),
            "negocio": m["negocio"],
            "creado_por": m["creado_por"],
            "hallazgos": report.get("hallazgos", []),
            "comparaciones": [{
                "nombre": row["nombre"],
                "actual": FormatUtils.format_currency(row["actual"]),
                "anterior": FormatUtils.format_currency(row["anterior"]),
                "diferencia": FormatUtils.format_currency(row["diferencia"]),
                "variacion": (
                    f"{row['porcentaje']:+.2f}%" if row["porcentaje"] is not None
                    else "No comparable"
                ),
            } for row in report.get("comparaciones", [])],
        }
        if "resumen" in report:
            summary = report["resumen"]
            result["resumen"] = {
                "ingresos": FormatUtils.format_currency(summary["ingresos"]),
                "gastos": FormatUtils.format_currency(summary["gastos"]),
                "saldo_movimientos": FormatUtils.format_currency(summary["saldo_movimientos"]),
                "ventas": FormatUtils.format_currency(summary["ventas"]),
                "ventas_realizadas": summary["ventas_realizadas"],
            }
        if "ventas" in report:
            sales = report["ventas"]
            result.update({
                "total_vendido": FormatUtils.format_currency(sales["total_vendido"]),
                "ticket_promedio": FormatUtils.format_currency(sales["ticket_promedio"]),
                "ventas_realizadas": sales["ventas_realizadas"],
                "grafica_evolucion": ReportCharts.evolution(
                    sales["evolucion"], temp / "ventas_evolucion.png", "Evolución de ventas"),
                "grafica_categorias": ReportCharts.categories(
                    sales["ventas_por_categoria"], temp / "ventas_categorias.png", "Ventas por categoría"),
                "grafica_productos": ReportCharts.categories(
                    sales["ventas_por_producto"], temp / "ventas_productos.png", "Productos y servicios más vendidos"),
            })
        if "ingresos" in report:
            inc = report["ingresos"]
            result.update({
                "total_ingresos": FormatUtils.format_currency(inc["total_ingresos"]),
                "categoria_mayor_ingreso": inc["categoria_mayor_ingreso"] or "Sin datos",
                "grafica_evolucion_ingresos": ReportCharts.evolution(
                    inc["evolucion"], temp / "ingresos_evolucion.png", "Evolución de ingresos"),
                "grafica_categorias_ingresos": ReportCharts.categories(
                    inc["ingresos_por_categoria"], temp / "ingresos_categorias.png", "Ingresos por categoría"),
                "ingresos_por_categoria": ReportDocumentService._categories(inc["ingresos_por_categoria"]),
            })
        if "gastos" in report:
            exp = report["gastos"]
            result.update({
                "total_gastos": FormatUtils.format_currency(exp["total_gastos"]),
                "categoria_mayor_gasto": exp["categoria_mayor_gasto"] or "Sin datos",
                "grafica_evolucion_gastos": ReportCharts.evolution(
                    exp["evolucion"], temp / "gastos_evolucion.png", "Evolución de gastos"),
                "grafica_categorias_gastos": ReportCharts.categories(
                    exp["gastos_por_categoria"], temp / "gastos_categorias.png", "Gastos por categoría"),
                "gastos_por_categoria": ReportDocumentService._categories(exp["gastos_por_categoria"]),
            })
        return result
    @staticmethod
    def _categories(categories: list[dict]) -> list[dict]:
        return [{
            "nombre": item["nombre"],
            "total": FormatUtils.format_currency(item["total"]),
            "porcentaje": FormatUtils.format_percentage(item["porcentaje"]),
        } for item in categories]
