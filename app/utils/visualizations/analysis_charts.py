
from collections import defaultdict
from datetime import date,datetime
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout

class AnalysisCharts:
    #*Gestiona las gráficas del módulo de análisis financiero
    def __init__(self,frame_ingresos_gastos,frame_distribucion,frame_evolucion,):
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
        figura = Figure(figsize=(8, 4))
        canvas = FigureCanvasQTAgg(figura)
        layout.addWidget(canvas)
        frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        frame.setMinimumHeight(400)
        return canvas

    @staticmethod
    def _formatear_monto(valor):
        return f"C$ {valor:,.2f}"
    @staticmethod
    def _mostrar_sin_datos(ax, mensaje="No hay datos para este período"):
        ax.clear()
        ax.text(
            0.5,
            0.5,
            mensaje,
            ha="center",
            va="center",
            transform=ax.transAxes,
            color="#777777",
            fontsize=10,
        )
        ax.set_axis_off()
    def actualizar(self, resultado):
        #*Actualiza las tres gráficas a partir del resultado devuelto por AnalysisService.
        periodo = resultado["period"]
        inicio = self._convertir_fecha(periodo["start_date"])
        fin = self._convertir_fecha(periodo["end_date"])
        rendimiento = resultado["charts"]["financial_performance"]
        gastos = resultado["categories"]["expenses"]
        self.graficar_ingresos_gastos(rendimiento, inicio, fin)
        self.graficar_distribucion_gastos(gastos)
        self.graficar_evolucion_balance(rendimiento, inicio, fin)
        self.graficar_distribucion_gastos(gastos)
        self.graficar_evolucion_balance(rendimiento, inicio, fin)

    def graficar_ingresos_gastos(self, datos, inicio, fin):
        canvas = self.canvas_ingresos_gastos
        figura = canvas.figure
        figura.clear()
        ax = figura.add_subplot(111)
        if not datos:
            self._mostrar_sin_datos(ax)
            self._ajustar_altura(self.frame_ingresos_gastos,tiene_datos=False,)
            figura.tight_layout()
            canvas.draw()
            return
        self._ajustar_altura(self.frame_ingresos_gastos,tiene_datos=True,)
        # Agrupar por mes cuando el período supera 31 días.
        agrupados = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
        for item in datos:
            intervalo = self._convertir_fecha(item["interval"])
            if (fin - inicio).days + 1 > 31:
                clave = intervalo.replace(day=1)
            else:
                clave = intervalo
            agrupados[clave]["income"] += float(item["income"])
            agrupados[clave]["expenses"] += float(item["expenses"])
        fechas = sorted(agrupados)
        ingresos = [agrupados[f]["income"] for f in fechas]
        gastos = [agrupados[f]["expenses"] for f in fechas]
        posiciones = list(range(len(fechas)))
        ancho = 0.38
        ax.bar(
            [p - ancho / 2 for p in posiciones],
            ingresos,
            width=ancho,
            label="Ingresos",
            color="#2E9D68",
        )
        ax.bar(
            [p + ancho / 2 for p in posiciones],
            gastos,
            width=ancho,
            label="Gastos",
            color="#E35D6A",
        )
        ax.set_xticks(posiciones)
        ax.set_xticklabels(
            [f.strftime("%d/%m") if len(fechas) <= 10
             else f.strftime("%d/%m") if (fin - inicio).days <= 31
             else f.strftime("%b %Y")
             for f in fechas],
            rotation=35,
            ha="right",
        )
        ax.set_ylabel("Monto (C$)")
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(
                lambda valor, _: f"C$ {valor:,.0f}"
            )
        )
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        ax.legend(frameon=False)

        figura.tight_layout()
        canvas.draw()

    def graficar_distribucion_gastos(self, datos):
        canvas = self.canvas_distribucion
        figura = canvas.figure
        figura.clear()
        ax = figura.add_subplot(111)

        categorias = [item["category"] for item in datos]
        montos = [float(item["amount"]) for item in datos]

        # Excluir importes nulos o negativos de la dona.
        pares = [
            (categoria, monto)
            for categoria, monto in zip(categorias, montos)
            if monto > 0
        ]

        if not pares:
            self._mostrar_sin_datos(ax, "No hay gastos para distribuir")
            self._ajustar_altura(self.frame_distribucion,tiene_datos=False,)
            figura.tight_layout()
            canvas.draw()
            return
        self._ajustar_altura(self.frame_distribucion,tiene_datos=True,)

        categorias, montos = zip(*pares)

        wedges, _, porcentajes = ax.pie(
            montos,
            startangle=90,
            counterclock=False,
            autopct=lambda porcentaje: (f"{porcentaje:.1f}%" if porcentaje >= 5 else ""),
            pctdistance=0.78,
            wedgeprops={
                "width": 0.42,
                "edgecolor": "white",
                "linewidth": 2,
            },
        )

        ax.legend(
            wedges,
            [
                f"{categoria} — {self._formatear_monto(monto)}"
                for categoria, monto in zip(categorias, montos)
            ],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.08),
            frameon=False,
            fontsize=8,
        )

        ax.set_aspect("equal")

        figura.tight_layout()
        canvas.draw()

    def graficar_evolucion_balance(self, datos, inicio, fin):
        canvas = self.canvas_evolucion
        figura = canvas.figure
        figura.clear()
        ax = figura.add_subplot(111)

        if not datos:
            self._mostrar_sin_datos(ax)
            self._ajustar_altura(self.frame_evolucion,tiene_datos=False,)
            figura.tight_layout()
            canvas.draw()
            return
        self._ajustar_altura(self.frame_evolucion,tiene_datos=True,)

        agrupados = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})

        for item in datos:
            intervalo = self._convertir_fecha(item["interval"])
            if (fin - inicio).days + 1 > 31:
                clave = intervalo.replace(day=1)
            else:
                clave = intervalo
            agrupados[clave]["income"] += float(item["income"])
            agrupados[clave]["expenses"] += float(item["expenses"])
        fechas = sorted(agrupados)
        balances = [
            agrupados[f]["income"] - agrupados[f]["expenses"]
            for f in fechas
        ]

        ax.plot(
            fechas,
            balances,
            color="#4776D0",
            linewidth=2,
            marker="o",
            markersize=4,
        )

        ax.axhline(
            y=0,
            color="#777777",
            linewidth=1,
            linestyle="--",
        )

        ax.fill_between(
            fechas,
            balances,
            0,
            where=[valor >= 0 for valor in balances],
            interpolate=True,
            color="#2E9D68",
            alpha=0.12,
        )
        ax.fill_between(
            fechas,
            balances,
            0,
            where=[valor < 0 for valor in balances],
            interpolate=True,
            color="#E35D6A",
            alpha=0.12,
        )

        if (fin - inicio).days + 1 <= 31:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        ax.set_ylabel("Balance (C$)")
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda valor, _: f"C$ {valor:,.0f}")
        )
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)

        figura.autofmt_xdate(rotation=35)
        figura.tight_layout()
        canvas.draw()

    @staticmethod
    def _convertir_fecha(valor):
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        if isinstance(valor, str):
            # Intervalo mensual: YYYY-MM
            if len(valor) == 7:
                return date.fromisoformat(f"{valor}-01")
            # Fecha completa: YYYY-MM-DD
            return date.fromisoformat(valor)
        raise TypeError(f"Tipo de fecha no válido: {type(valor).__name__}")
    def _ajustar_altura(self, frame, tiene_datos):
        altura = 700 if tiene_datos else 150
        frame.setMinimumHeight(altura)
        frame.setMaximumHeight(altura)