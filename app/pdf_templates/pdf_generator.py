from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from weasyprint import HTML, CSS

class PdfGenerator:
    TIPOS_VALIDOS = {"ventas", "ingresos", "gastos", "general"}
    def __init__(self):
        self.templates_dir = Path(__file__).resolve().parent
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            undefined=StrictUndefined,
        )
    def generate_report(self, data: dict) -> bytes:
        report_type = data.get("tipo_reporte")
        if report_type not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de informe no válido: {report_type}")
        html = self.env.get_template("reporte_maestro.html").render(**data)
        stylesheet = CSS(filename=str(self.templates_dir / "styles" / "reporte_v2.css"))
        return HTML(string=html, base_url=self.templates_dir.as_uri() + "/").write_pdf(
            stylesheets=[stylesheet]
        )
