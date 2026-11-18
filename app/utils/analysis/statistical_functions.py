from decimal import Decimal, InvalidOperation, localcontext
import math

class StatisticalFunctions:
    @staticmethod
    def calculate_mean(coleccion):
        valores = [Decimal(str(x)) for x in coleccion]
        return float(sum(valores) / len(valores)) if valores else None
    @staticmethod
    def calculate_population_std(coleccion):
        valores = [Decimal(str(x)) for x in coleccion]
        if not valores:
            return None
        with localcontext() as ctx:
            ctx.prec = 34
            media = sum(valores) / len(valores)
            varianza = sum((x - media) ** 2 for x in valores) / len(valores)
            return float(varianza.sqrt())
    @staticmethod
    def calculate_coefficient_variation(media, desvEst):
        if media is None or desvEst is None:
            return None
        if not math.isfinite(float(media)) or not math.isfinite(float(desvEst)):
            return None
        if media <= 0 or desvEst < 0:
            return None
        return round((desvEst / media) * 100, 2)
    @staticmethod
    def classify_coefficient_variation(cv):
        if cv is None or not math.isfinite(float(cv)) or cv < 0:
            return None
        if cv <= 15:
            return "Variabilidad Baja"
        if cv <= 30:
            return "Variabilidad Moderada"
        return "Variabilidad Alta"
    @staticmethod
    def from_aggregates(count, total, sum_squares):
        #*Calcula media/desviación poblacional usando agregaciones SQL.
        n = int(count or 0)
        if n <= 0:
            return {"mean": None, "std": None, "coefficient_variation": None,
                    "classification": None}
        with localcontext() as ctx:
            ctx.prec = 40
            s = Decimal(str(total or 0))
            squares = Decimal(str(sum_squares or 0))
            mean = s / Decimal(n)
            if n < 2:
                return {"mean": float(mean), "std": None,
                        "coefficient_variation": None, "classification": None}
            variance = (squares / Decimal(n)) - (mean * mean)
            # Redondeos decimales microscópicos pueden volver negativo el cero.
            variance = max(variance, Decimal(0))
            std = variance.sqrt()
            cv = StatisticalFunctions.calculate_coefficient_variation(float(mean), float(std))
            return {"mean": float(mean), "std": float(std),
                    "coefficient_variation": cv,
                    "classification": StatisticalFunctions.classify_coefficient_variation(cv)}
