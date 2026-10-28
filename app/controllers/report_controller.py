from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QFileDialog,QMessageBox,)
from app.services.report_service import ReportService
from app.utils.format_utils import FormatUtils
from app.pdf_templates.pdf_generator import PdfGenerator

class ReportController:
    def __init__(self, report_service=None, pdf_generator=None):
        self.report_service = report_service or ReportService()
        self.pdf_generator = pdf_generator or PdfGenerator()
    #*Flujo principal
    def generar_informe(self, datos: dict, parent=None):
        try:
            report_data = self.report_service.get_report_data(datos)
            with TemporaryDirectory(prefix="finanzen_report_") as temp_dir:
                temp_path = Path(temp_dir)
                pdf_data = self._prepare_pdf_data(report_data,temp_path,)
                pdf_bytes = self.pdf_generator.generate_report(pdf_data)
                if not pdf_bytes:
                    raise RuntimeError("El generador no devolvió contenido PDF.")
                file_path, _ = QFileDialog.getSaveFileName(
                    parent,
                    "Guardar informe PDF",
                    self._default_filename(report_data),
                    "Documento PDF (*.pdf)",
                )
                # Cancelar el diálogo no es un error.
                if not file_path:
                    return False
                if not file_path.lower().endswith(".pdf"):
                    file_path += ".pdf"
                with open(file_path, "wb") as pdf_file:
                    pdf_file.write(pdf_bytes)
            QMessageBox.information(parent,"Informe generado","El informe PDF se guardó correctamente.",)
            return True
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(parent,"No se pudo generar el informe",str(exc),)
            return False
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Error al generar el informe PDF")
            QMessageBox.critical(
                parent,"Error","Ocurrió un error al generar o guardar el informe PDF.",
            )
            return False
    #*Preparación del diccionario para Jinja2
    def _prepare_pdf_data(self,report_data: dict,temp_path: Path,) -> dict:
        metadata = report_data["metadata"]
        start_date = metadata["fecha_inicio"]
        end_date = metadata["fecha_fin"]
        data = {
            "tipo_reporte": metadata["tipo_reporte"],
            "periodo_inicio": FormatUtils.format_report_date(start_date),
            "periodo_fin": FormatUtils.format_report_date(end_date),
            "negocio": metadata["negocio"],
            "creado_por": metadata["creado_por"],
        }
        if "ventas" in report_data:
            data.update(self._prepare_sales(report_data["ventas"],temp_path,))
        if "ingresos" in report_data:
            data.update(self._prepare_income(report_data["ingresos"],temp_path,))
        if "gastos" in report_data:
            data.update(self._prepare_expenses(report_data["gastos"],temp_path,))
        return data
    #*Ventas
    def _prepare_sales(self, sales: dict, temp_path: Path) -> dict:
        evolution_chart = self._create_evolution_chart(
            sales["evolucion"],temp_path / "ventas_evolucion.png","Evolución de ventas",
        )
        category_chart = self._create_category_chart(
            sales["ventas_por_categoria"],temp_path / "ventas_categorias.png","Ventas por categoría",
        )
        product_chart = self._create_category_chart(
            sales["ventas_por_producto"],temp_path / "ventas_productos.png","Top 10 de productos y servicios",
        )
        return {
            "total_vendido": FormatUtils.format_currency(sales["total_vendido"]),
            "ticket_promedio": FormatUtils.format_currency(sales["ticket_promedio"]),
            "ventas_realizadas": sales["ventas_realizadas"],
            "grafica_evolucion": evolution_chart,
            "grafica_categorias": category_chart,
            "grafica_productos": product_chart,
        }
    #*Ingresos
    def _prepare_income(self, income: dict, temp_path: Path) -> dict:
        evolution_chart = self._create_evolution_chart(
            income["evolucion"],temp_path / "ingresos_evolucion.png","Evolución de ingresos",
        )
        category_chart = self._create_category_chart(
            income["ingresos_por_categoria"],temp_path / "ingresos_categorias.png","Ingresos por categoría",
        )
        categories = [
            {
                "nombre": item["nombre"],
                "total": FormatUtils.format_currency(item["total"]),
                "porcentaje": FormatUtils.format_percentage(item["porcentaje"]),
            }
            for item in income["ingresos_por_categoria"]
        ]
        return {
            "total_ingresos": FormatUtils.format_currency(
                income["total_ingresos"]
            ),
            "categoria_mayor_ingreso": (
                income["categoria_mayor_ingreso"] or "Sin datos"
            ),
            "grafica_evolucion_ingresos": evolution_chart,
            "grafica_categorias_ingresos": category_chart,
            "ingresos_por_categoria": categories,
        }
    #*Gastos
    def _prepare_expenses(self, expenses: dict, temp_path: Path) -> dict:
        evolution_chart = self._create_evolution_chart(
            expenses["evolucion"],temp_path / "gastos_evolucion.png","Evolución de gastos",
        )
        category_chart = self._create_category_chart(
            expenses["gastos_por_categoria"],temp_path / "gastos_categorias.png","Gastos por categoría",
        )
        categories = [
            {
                "nombre": item["nombre"],
                "total": FormatUtils.format_currency(item["total"]),
                "porcentaje": FormatUtils.format_percentage(item["porcentaje"]),
            }
            for item in expenses["gastos_por_categoria"]
        ]
        return {
            "total_gastos": FormatUtils.format_currency(expenses["total_gastos"]),
            "categoria_mayor_gasto": (expenses["categoria_mayor_gasto"] or "Sin datos"),
            "grafica_evolucion_gastos": evolution_chart,
            "grafica_categorias_gastos": category_chart,
            "gastos_por_categoria": categories,
        }
    #*Gráficas
    @staticmethod
    def _create_evolution_chart(evolution: list[dict],output_path: Path,title: str,) -> str:
        if not evolution:
            return ""
        labels = []
        values = []
        for item in evolution:
            start = item["fecha_inicio"]
            end = item["fecha_fin"]
            if start == end:
                label = FormatUtils.short_date(start)
            else:
                label = (
                    f"{FormatUtils.short_date(start)} - "
                    f"{FormatUtils.short_date(end)}"
                )
            labels.append(label)
            values.append(float(item["total"]))
        fig, ax = plt.subplots(figsize=(9, 3.5))
        try:
            color = "#744BCC"
            ax.plot(
                range(len(values)),
                values,
                marker="o",
                linewidth=2,
                markersize=5,
                color=color,
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=1,
            )
            ax.set_title(
                title,
                color="#343047",
                fontsize=12,
                fontweight="bold",
            )
            ax.set_ylabel("Monto (C$)", color="#5E5A6E")
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(
                labels,
                rotation=45,
                ha="right",
                fontsize=8,
                color="#5E5A6E",
            )
            ax.tick_params(axis="y", colors="#5E5A6E")
            ax.grid(
                axis="y",
                color="#E8E5EF",
                linewidth=0.8,
                alpha=0.8,
            )
            ax.set_axisbelow(True)
            # Ocultar bordes superiores y derechos
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E8E5EF")
            ax.spines["bottom"].set_color("#E8E5EF")
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")
            fig.tight_layout()
            fig.savefig(
                output_path,
                dpi=150,
                bbox_inches="tight",
                facecolor="white",
            )
        finally:
            plt.close(fig)
        return output_path.resolve().as_uri()

    @staticmethod
    def _create_category_chart(categories: list[dict],output_path: Path,title: str,) -> str:
        if not categories:
            return ""
        names = [item["nombre"] for item in categories]
        values = [float(item["total"]) for item in categories]
        fig, ax = plt.subplots(figsize=(8, 4))
        try:
            ax.barh(
                names[::-1],
                values[::-1],
                color="#744BCC",
                height=0.65,
            )
            ax.set_title(
                title,
                color="#343047",
                fontsize=12,
                fontweight="bold",
            )
            ax.set_xlabel("Monto (C$)", color="#5E5A6E")
            ax.tick_params(axis="both", colors="#5E5A6E")
            ax.grid(
                axis="x",
                color="#E8E5EF",
                linewidth=0.8,
                alpha=0.8,
            )
            ax.set_axisbelow(True)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E8E5EF")
            ax.spines["bottom"].set_color("#E8E5EF")
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")
            fig.tight_layout()
            fig.savefig(
                output_path,
                dpi=150,
                bbox_inches="tight",
                facecolor="white",
            )
        finally:
            plt.close(fig)
        return output_path.resolve().as_uri()

    #*Nombre predeterminado del archivo
    @staticmethod
    def _default_filename(report_data: dict) -> str:
        metadata = report_data["metadata"]
        start = metadata["fecha_inicio"].strftime("%Y%m%d")
        end = metadata["fecha_fin"].strftime("%Y%m%d")
        report_type = metadata["tipo_reporte"]
        return f"Finanzen_{report_type}_{start}_{end}.pdf"
