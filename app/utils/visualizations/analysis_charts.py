#Gráficas Matplotlib/Qt del módulo Análisis
from collections import defaultdict
from datetime import date, datetime, timedelta
from calendar import monthrange

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy


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
        canvas = FigureCanvasQTAgg(Figure(figsize=(7, 3.5), dpi=100))
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
        """Rellena intervalos sin movimientos como cero, sin inventar operaciones."""
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
        ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes,
                fontsize=10, color="#777777")
        ax.axis("off")

    @staticmethod
    def _money_axis(ax):
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"C$ {x:,.0f}"))
        ax.grid(axis="y", alpha=0.18)
        ax.set_axisbelow(True)

    @staticmethod
    def _finish(canvas):
        canvas.figure.tight_layout(pad=1.5)
        canvas.draw_idle()

    def mostrar_vacio(self, message="Sin datos para mostrar"):
        for canvas in (self.canvas_ingresos_gastos, self.canvas_distribucion, self.canvas_evolucion):
            canvas.figure.clear()
            self._empty(canvas.figure.add_subplot(111), message)
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
        fechas, ingresos, gastos, monthly = self._series(datos, inicio, fin)
        if not fechas:
            self._empty(ax, "Sin ingresos ni gastos en este período")
        else:
            xs = list(range(len(fechas)))
            w = 0.38
            ax.bar([x - w / 2 for x in xs], ingresos, width=w, label="Ingresos", color="#2E9D68")
            ax.bar([x + w / 2 for x in xs], gastos, width=w, label="Gastos", color="#E35D6A")
            step = max(1, (len(xs) + 9) // 10)
            ticks = xs[::step]
            ax.set_xticks(ticks, [fechas[i].strftime("%b %Y" if monthly else "%d/%m") for i in ticks],
                            rotation=35, ha="right")
            ax.set_ylabel("Monto (C$)")
            self._money_axis(ax)
            ax.legend(frameon=False)
        self._finish(canvas)

    def graficar_distribucion_gastos(self, datos):
        canvas = self.canvas_distribucion
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        pares = [(str(x["category"]), float(x["amount"])) for x in datos if float(x["amount"]) > 0]
        if not pares:
            self._empty(ax, "Sin gastos para distribuir")
        else:
            categorias, montos = zip(*pares)
            slices, _, _ = ax.pie(montos, startangle=90, counterclock=False,
                                    autopct=lambda p: f"{p:.1f}%" if p >= 5 else "",
                                    pctdistance=0.78,
                                    wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2})
            ax.legend(slices, [f"{cat} — C$ {amount:,.2f}" for cat, amount in pares],
                        loc="lower center", bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=8)
            ax.set_aspect("equal")
        self._finish(canvas)

    def graficar_evolucion_balance(self, datos, inicio, fin):
        canvas = self.canvas_evolucion
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        fechas, ingresos, gastos, monthly = self._series(datos, inicio, fin)
        if not fechas:
            self._empty(ax, "Sin movimientos para calcular balances")
        else:
            balances = [inc - exp for inc, exp in zip(ingresos, gastos)]
            ax.plot(fechas, balances, color="#4776D0", linewidth=2, marker="o", markersize=3)
            ax.axhline(0, color="#777777", linewidth=1, linestyle="--")
            ax.fill_between(fechas, balances, 0, where=[v >= 0 for v in balances],
                            color="#2E9D68", alpha=0.12)
            ax.fill_between(fechas, balances, 0, where=[v < 0 for v in balances],
                            color="#E35D6A", alpha=0.12)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y" if monthly else "%d/%m"))
            ax.set_ylabel("Balance del intervalo (C$)")
            self._money_axis(ax)
            canvas.figure.autofmt_xdate(rotation=35)
        self._finish(canvas)
