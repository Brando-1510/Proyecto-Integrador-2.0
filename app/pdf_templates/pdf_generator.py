from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class PdfGenerator:
    TIPOS_VALIDOS = {
        "ventas",
        "ingresos",
        "gastos",
        "general",
    }
    def __init__(self):
        self.templates_dir = Path(__file__).resolve().parent
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
    def generate_report(self, data: dict) -> bytes:
        tipo_reporte = data.get("tipo_reporte")
        if tipo_reporte not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de informe no válido: {tipo_reporte}")
        template = self.env.get_template("reporte_maestro.html")
        html = template.render(**data)
        return HTML(string=html,base_url=str(self.templates_dir)).write_pdf()