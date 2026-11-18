from collections import defaultdict
from datetime import date, datetime, timedelta
import math
import textwrap
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy

# Identidad de Finanzen y colores semánticos compartidos con sus reportes.
PLUM_DARK = "#281027"
PLUM = "#3B153A"
PLUM_MEDIUM = "#60305F"
PLUM_SOFT = "#99729A"
LILAC = "#C1A2C2"
AMBER = "#E9A96D"
OTHER = "#D8CFD9"
POSITIVE = "#287A55"
NEGATIVE = "#B23B52"
MUTED = "#746B74"
BORDER = "#E3DCE4"
WHITE = "#FFFFFF"
EXPENSE_COLORS = [PLUM_MEDIUM, PLUM_SOFT, LILAC, AMBER, OTHER]

class AnalysisCharts:
    def __init__(self, frame_ingresos_gastos, frame_distribucion, frame_evolucion):
        self.frame_ingresos_gastos = frame_ingresos_gastos
        self.frame_distribucion = frame_distribucion
        self.frame_evolucion = frame_evolucion
        self.canvas_ingresos_gastos = self._crear_canvas(frame_ingresos_gastos)
        self.canvas_distribucion = self._crear_canvas(frame_distribucion)
        self.canvas_evolucion = self._crear_canvas(frame_evolucion)

    @staticmethod
    def _crear_canvas(frame):
        layout = frame.layout()
        if layout is None:
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(8, 8, 8, 8)

        fig = Figure(figsize=(7, 3.5), dpi=100, facecolor=WHITE)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(canvas)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame.setFixedHeight(350)
        return canvas

    @staticmethod
    def _convertir_fecha(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value + "-01" if len(value) == 7 else value)
        raise ValueError("Fecha de gráfico inválida")

    @staticmethod
    def _series(datos, inicio, fin):
        """Rellena intervalos sin movimientos con 0, sin inventar operaciones."""
        monthly = (fin - inicio).days + 1 > 31
        values = defaultdict(lambda: [0.0, 0.0])
        for item in datos:
            f = AnalysisCharts._convertir_fecha(item["interval"])
            key = f.replace(day=1) if monthly else f
            values[key][0] += float(item["income"])
            values[key][1] += float(item["expenses"])
        if not values:
            return [], [], [], monthly

        current = inicio.replace(day=1) if monthly else inicio
        end = fin.replace(day=1) if monthly else fin
        dates, income, expenses = [], [], []
        while current <= end:
            dates.append(current)
            inc, exp = values[current]
            income.append(inc)
            expenses.append(exp)
            if monthly:
                current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                current += timedelta(days=1)
        return dates, income, expenses, monthly

    @staticmethod
    def _empty(ax, message):
        ax.text(0.5, 0.5, message, ha="center", va="center",
                transform=ax.transAxes, fontsize=10, color=MUTED)
        ax.axis("off")

    @staticmethod
    def _money_axis(ax):
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"C$ {x:,.0f}")
        )
        ax.grid(axis="y", color=BORDER, linewidth=0.8, alpha=0.8)
        ax.set_axisbelow(True)

    @staticmethod
    def _style_axis(ax):
        ax.set_facecolor(WHITE)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color(BORDER)
        ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0)
        ax.yaxis.label.set_color(PLUM_DARK)

    @staticmethod
    def _finish(canvas, auto_layout=True):
        # La dona utiliza ejes con coordenadas manuales; tight_layout los alteraría.
        if auto_layout:
            canvas.figure.tight_layout(pad=1.7)
        canvas.draw_idle()

    def mostrar_vacio(self, message="Sin datos para mostrar"):
        for canvas in (
            self.canvas_ingresos_gastos,
            self.canvas_distribucion,
            self.canvas_evolucion,
        ):
            canvas.figure.clear()
            ax = canvas.figure.add_subplot(111)
            self._empty(ax, message)
            self._finish(canvas)

    def actualizar(self, resultado):
        period = resultado["period"]
        inicio = self._convertir_fecha(period["start_date"])
        fin = self._convertir_fecha(period["end_date"])
        performance = resultado["charts"]["financial_performance"]
        expenses = resultado["categories"]["expenses"]

        self.graficar_ingresos_gastos(performance, inicio, fin)
        self.graficar_distribucion_gastos(expenses)
        self.graficar_evolucion_balance(performance, inicio, fin)

    def graficar_ingresos_gastos(self, datos, inicio, fin):
        canvas = self.canvas_ingresos_gastos
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        self._style_axis(ax)
        fechas, ingresos, gastos, monthly = self._series(datos, inicio, fin)
        if not fechas:
            self._empty(ax, "Sin ingresos ni gastos en este período")
        else:
            xs = list(range(len(fechas)))
            w = 0.38
            ax.bar([x - w / 2 for x in xs], ingresos, width=w,
                   label="Ingresos", color=POSITIVE)
            ax.bar([x + w / 2 for x in xs], gastos, width=w,
                   label="Gastos", color=NEGATIVE)
            step = max(1, (len(xs) + 9) // 10)
            ticks = xs[::step]
            ax.set_xticks(ticks, [
                fechas[i].strftime("%b %Y" if monthly else "%d/%m")
                for i in ticks
            ], rotation=35, ha="right")
            ax.set_ylabel("Monto (C$)")
            self._money_axis(ax)
            ax.legend(frameon=False, labelcolor=PLUM_DARK, fontsize=9)
        self._finish(canvas)

    @staticmethod
    def _agrupar_gastos(datos):
        """Muestra hasta 4 categorías principales y agrupa el resto si hay >5.

        La agrupación afecta solo a la visualización, nunca a los datos
        calculados ni al total de gastos.
        """
        pares = []
        for item in datos:
            try:
                cantidad = float(item.get("amount") or 0)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(cantidad) or cantidad <= 0:
                continue
            nombre = str(item.get("category") or "Sin categoría").strip()
            pares.append((nombre or "Sin categoría", cantidad))

        pares.sort(key=lambda par: par[1], reverse=True)
        if len(pares) <= 5:
            return pares, 0
        restantes = pares[4:]
        return pares[:4] + [("Otras categorías", sum(v for _, v in restantes))], len(restantes)

    def graficar_distribucion_gastos(self, datos):
        """Dona a la izquierda; leyenda con importes reales a la derecha."""
        canvas = self.canvas_distribucion
        figura = canvas.figure
        figura.clear()
        figura.set_facecolor(WHITE)

        grupos, numero_agrupadas = self._agrupar_gastos(datos)
        if not grupos:
            ax = figura.add_subplot(111)
            self._empty(ax, "Sin gastos para distribuir")
            self._finish(canvas)
            return

        # Dos áreas independientes impiden la superposición de leyenda y dona.
        ax_dona = figura.add_axes([0.025, 0.09, 0.405, 0.83])
        ax_leyenda = figura.add_axes([0.465, 0.10, 0.505, 0.80])
        ax_dona.axis("off")
        ax_leyenda.axis("off")
        ax_leyenda.set_xlim(0, 1)
        ax_leyenda.set_ylim(0, 1)

        montos = [cantidad for _, cantidad in grupos]
        colores = EXPENSE_COLORS[:len(grupos)]
        total = sum(montos)
        ax_dona.pie(
            montos,
            colors=colores,
            startangle=90,
            counterclock=False,
            radius=0.98,
            wedgeprops={
                "width": 0.34,
                "edgecolor": WHITE,
                "linewidth": 2.2,
            },
        )
        ax_dona.set_aspect("equal")

        # KPI central: porcentaje de la categoría de mayor gasto.
        # El total se toma de los valores originales agregados, sin alterar.
        top_nombre, top_importe = grupos[0]
        porcentaje_lider = top_importe / total * 100
        ax_dona.text(0, 0.20, "Mayor gasto", ha="center", va="center",
                     fontsize=10.5, color=MUTED, weight="medium")
        ax_dona.text(0, -0.02, f"{porcentaje_lider:.2f}%",
                     ha="center", va="center", fontsize=22,
                     color=PLUM_DARK, weight="bold")
        ax_dona.text(0, -0.25,
                     textwrap.shorten(top_nombre, width=19, placeholder="…"),
                     ha="center", va="center", fontsize=9, color=PLUM_MEDIUM)

        # Cinco filas como máximo; dos líneas por categoría permiten mostrar
        # el nombre, su porcentaje y el importe sin amontonar información.
        inicio_y = 0.88 - (5 - len(grupos)) * 0.075
        for i, ((categoria, cantidad), color) in enumerate(zip(grupos, colores)):
            y = inicio_y - i * 0.18
            porcentaje = cantidad / total * 100
            etiqueta = textwrap.shorten(categoria, width=29, placeholder="…")
            ax_leyenda.scatter([0.035], [y], s=62, color=color, marker="s",
                               edgecolors="none", zorder=3)
            ax_leyenda.text(0.085, y + 0.016, etiqueta,
                            fontsize=10, color=PLUM_DARK, va="center",
                            ha="left", weight="medium")
            ax_leyenda.text(0.97, y + 0.016, f"{porcentaje:.2f}%",
                            fontsize=10, color=PLUM_DARK, va="center",
                            ha="right", weight="bold")
            ax_leyenda.text(0.085, y - 0.057, f"C$ {cantidad:,.2f}",
                            fontsize=8.5, color=MUTED, va="center", ha="left")

        if numero_agrupadas:
            ax_leyenda.text(0.085, 0.02,
                            f"Otras categorías agrupa {numero_agrupadas} categorías",
                            fontsize=8, color=MUTED, va="center", ha="left")

        # Importante: NO usar tight_layout en estos ejes posicionados a mano.
        self._finish(canvas, auto_layout=False)

    def graficar_evolucion_balance(self, datos, inicio, fin):
        canvas = self.canvas_evolucion
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        self._style_axis(ax)
        fechas, ingresos, gastos, monthly = self._series(datos, inicio, fin)
        if not fechas:
            self._empty(ax, "Sin movimientos para calcular balances")
        else:
            balances = [inc - exp for inc, exp in zip(ingresos, gastos)]
            ax.plot(fechas, balances, color=PLUM_MEDIUM,
                    linewidth=2.1, marker="o", markersize=3)
            ax.axhline(0, color=MUTED, linewidth=1, linestyle="--")
            ax.fill_between(fechas, balances, 0,
                            where=[v >= 0 for v in balances],
                            color=POSITIVE, alpha=0.12)
            ax.fill_between(fechas, balances, 0,
                            where=[v < 0 for v in balances],
                            color=NEGATIVE, alpha=0.12)
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter("%b %Y" if monthly else "%d/%m")
            )
            ax.set_ylabel("Balance del intervalo (C$)")
            self._money_axis(ax)
            canvas.figure.autofmt_xdate(rotation=35)
        self._finish(canvas)
