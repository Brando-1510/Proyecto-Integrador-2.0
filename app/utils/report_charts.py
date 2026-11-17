#*Gráficas de los informes PDF; no depende de objetos de PySide6
from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.utils.format_utils import FormatUtils

PLUM = "#60305F"
TEXT = "#3B153A"
GRID = "#E3DCE4"


class ReportCharts:
    @staticmethod
    def evolution(rows: list[dict], destination: Path, title: str) -> str:
        if not rows:
            return ""
        labels = []
        values = []
        for row in rows:
            start, end = row["fecha_inicio"], row["fecha_fin"]
            labels.append(FormatUtils.short_date(start) if start == end else
                        f"{FormatUtils.short_date(start)} – {FormatUtils.short_date(end)}")
            values.append(float(row["total"]))
        fig, ax = plt.subplots(figsize=(9, 3.1))
        try:
            x = list(range(len(values)))
            ax.plot(x, values, color=PLUM, linewidth=2.1, marker="o", markersize=3.5)
            ax.set_title(title, fontsize=12, color=TEXT, weight="semibold", pad=12)
            ax.set_ylabel("Monto (C$)", fontsize=9, color=TEXT)
            # No imprimir 52 etiquetas encima de otras.
            step = max(1, math.ceil(len(labels) / 9))
            ticks = list(range(0, len(labels), step))
            if ticks[-1] != len(labels) - 1:
                ticks.append(len(labels) - 1)
            ax.set_xticks(ticks, [labels[i] for i in ticks], rotation=30, ha="right", fontsize=8)
            ax.grid(axis="y", color=GRID, alpha=0.8)
            ax.set_axisbelow(True)
            ax.tick_params(colors=TEXT, labelsize=8)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("bottom", "left"):
                ax.spines[side].set_color(GRID)
            fig.tight_layout()
            fig.savefig(destination, dpi=140, bbox_inches="tight", facecolor="white")
        finally:
            plt.close(fig)
        return destination.resolve().as_uri()

    @staticmethod
    def categories(rows: list[dict], destination: Path, title: str, limit: int = 10) -> str:
        if not rows:
            return ""
        # Barras legibles; el informe numérico completo permanece en la tabla.
        selection = rows[:limit]
        names = [str(row["nombre"] or "Sin categoría")[:35] for row in selection]
        amounts = [float(row["total"]) for row in selection]
        height = max(2.8, min(5.7, len(selection) * 0.42 + 1.4))
        fig, ax = plt.subplots(figsize=(8.4, height))
        try:
            ax.barh(names[::-1], amounts[::-1], color=PLUM, height=0.62)
            ax.set_title(title, fontsize=12, color=TEXT, weight="semibold", pad=12)
            ax.set_xlabel("Monto (C$)", fontsize=9, color=TEXT)
            ax.grid(axis="x", color=GRID, alpha=0.8)
            ax.set_axisbelow(True)
            ax.tick_params(colors=TEXT, labelsize=8)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("bottom", "left"):
                ax.spines[side].set_color(GRID)
            fig.tight_layout()
            fig.savefig(destination, dpi=140, bbox_inches="tight", facecolor="white")
        finally:
            plt.close(fig)
        return destination.resolve().as_uri()
