import math
class FindingFunctions:
    # *ormatea un importe para incluirlo en una descripción.
    @staticmethod
    def _format_amount(value: int | float) -> str:
        return f"{value:,.2f}"

    #*Formatea un porcentaje o indica que no está disponible.
    @staticmethod
    def _format_percentage(value: float | None) -> str:
        if value is None:
            return "no disponible"
        return f"{value:.2f}%"

    #*Construye un hallazgo a partir del análisis de variación de los gastos.
    @staticmethod
    def build_expense_finding(result: dict) -> dict:
        current = result["current_value"]
        previous = result["previous_value"]
        absolute = result["absolute_variation"]
        percentage = result["percentage_variation"]
        direction = result["direction"]
        relevant = result["is_relevant"]
        if relevant is None:
            title = "Variación de gastos no determinada"
            description = (
                f"Los gastos presentan una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}. "
                "No se puede determinar la relevancia porcentual "
                "del cambio porque la variación porcentual "
                "no está disponible."
            )
        elif not relevant:
            title = "Variación de gastos no relevante"
            description = (
                f"Los gastos registraron una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}, "
                f"equivalente al "
                f"{FindingFunctions._format_percentage(percentage)}. "
                "El cambio no alcanza el umbral de relevancia definido."
            )
        else:
            title = (
                "Aumento relevante de gastos"
                if absolute > 0
                else "Disminución relevante de gastos"
            )
            description = (
                f"Los gastos registraron una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}, "
                f"equivalente al "
                f"{FindingFunctions._format_percentage(percentage)}. "
                "El cambio alcanza el umbral de relevancia definido."
            )
        return {
            "type": "expense_variation",
            "title": title,
            "description": description,
            "data": {
                "current_value": current,
                "previous_value": previous,
                "absolute_variation": absolute,
                "percentage_variation": percentage,
                "direction": direction,
                "is_relevant": relevant
            }
        }

    #*Construye un hallazgo a partir del análisis de variación de los ingresos.
    @staticmethod
    def build_income_finding(result: dict) -> dict:
        current = result["current_value"]
        previous = result["previous_value"]
        absolute = result["absolute_variation"]
        percentage = result["percentage_variation"]
        direction = result["direction"]
        relevant = result["is_relevant"]
        if relevant is None:
            title = "Variación de ingresos no determinada"
            description = (
                f"Los ingresos presentan una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}. "
                "No se puede determinar la relevancia porcentual "
                "del cambio porque la variación porcentual "
                "no está disponible."
            )
        elif not relevant:
            title = "Variación de ingresos no relevante"
            description = (
                f"Los ingresos registraron una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}, "
                f"equivalente al "
                f"{FindingFunctions._format_percentage(percentage)}. "
                "El cambio no alcanza el umbral de relevancia definido."
            )
        else:
            title = (
                "Aumento relevante de ingresos"
                if absolute > 0
                else "Disminución relevante de ingresos"
            )
            description = (
                f"Los ingresos registraron una {direction.lower()} "
                f"de {FindingFunctions._format_amount(abs(absolute))}, "
                f"equivalente al "
                f"{FindingFunctions._format_percentage(percentage)}. "
                "El cambio alcanza el umbral de relevancia definido."
            )
        return {
            "type": "income_variation",
            "title": title,
            "description": description,
            "data": {
                "current_value": current,
                "previous_value": previous,
                "absolute_variation": absolute,
                "percentage_variation": percentage,
                "direction": direction,
                "is_relevant": relevant
            }
        }

    #* Construye un hallazgo a partir del análisis estadístico de la variabilidad de las ventas.
    @staticmethod
    def build_sales_variability_finding(result: dict) -> dict:
        mean = result["mean"]
        std = result["std"]
        cv = result["coefficient_variation"]
        classification = result["classification"]
        if cv is None or classification is None:
            title = "Variabilidad de ventas no determinada"
            description = (
                "No fue posible determinar la variabilidad de las ventas con los datos disponibles."
            )
        else:
            title = f"Variabilidad de ventas: {classification.lower()}"
            description = (
                f"Las ventas presentan una {classification.lower()}, "
                f"con un coeficiente de variación del {cv:.2f}%. "
                f"La media de ventas es "
                f"{FindingFunctions._format_amount(mean)} y la "
                f"desviación estándar es "
                f"{FindingFunctions._format_amount(std)}."
            )
        return {
            "type": "sales_variability",
            "title": title,
            "description": description,
            "data": {
                "mean": mean,
                "std": std,
                "coefficient_variation": cv,
                "classification": classification
            }
        }

    # *Calcula el porcentaje que representa una categoría respecto al total.
    @staticmethod
    def calculate_category_percentage(amount: int | float, total: int | float) -> float | None:
        if total <= 0:
            return None
        return round((amount / total) * 100, 2)

    # *Analiza la categoría o categorías con el mayor importe.
    @staticmethod
    def _analyze_category(categories: list[dict]) -> dict | None:
        if not categories:
            return None
        try:
            normalized = [
                {"category": item["category"], "amount": float(item["amount"])}
                for item in categories
            ]
        except (KeyError, TypeError, ValueError):
            return None
        if any(
            not isinstance(item["category"], str)
            or not item["category"].strip()
            or not math.isfinite(item["amount"])
            or item["amount"] < 0
            for item in normalized
        ):
            return None
        total = sum(item["amount"] for item in normalized)
        if total <= 0:
            return None
        maximum = max(item["amount"] for item in normalized)
        top_categories = [
            item["category"] for item in normalized
            if item["amount"] == maximum
        ]
        percentage = FindingFunctions.calculate_category_percentage(maximum, total)
        if percentage is None:
            return None
        return {
            "categories": top_categories,
            "amount": maximum,
            "total": total,
            "percentage": percentage
        }

    # *Identifica la categoría con el mayor importe total de gastos.
    @staticmethod
    def analyze_expense_category(categories: list[dict]) -> dict | None:
        return FindingFunctions._analyze_category(categories)

    # *Identifica la categoría con el mayor importe total de ingresos.
    @staticmethod
    def analyze_income_category(categories: list[dict]) -> dict | None:
        return FindingFunctions._analyze_category(categories)

    # *Identifica la categoría con el mayor importe total de ventas.
    @staticmethod
    def analyze_sales_category(categories: list[dict]) -> dict | None:
        return FindingFunctions._analyze_category(categories)

    # *Construye un hallazgo a partir del análisis de la categoría principal.
    @staticmethod
    def _build_category_finding(result: dict | None, finding_type: str, title: str, amount_label: str) -> dict | None:
        if result is None:
            return None
        categories = result["categories"]
        category_text = ", ".join(categories)
        amount = result["amount"]
        percentage = result["percentage"]
        description = (
            f"{category_text} representa el "
            f"{FindingFunctions._format_percentage(percentage)} del total de "
            f"{amount_label}, con un importe de C$ "
            f"{FindingFunctions._format_amount(amount)}."
        )
        return {
            "type": finding_type,
            "title": title,
            "description": description,
            "data": {
                "categories": categories,
                "amount": amount,
                "total": result["total"],
                "percentage": percentage
            }
        }

    # *Construye un hallazgo a partir del análisis de la categoría con mayor gasto.
    @staticmethod
    def build_expense_category_finding(result: dict | None) -> dict | None:
        return FindingFunctions._build_category_finding(
            result, "expense_category", "Mayor categoría de gastos", "gastos"
        )

    # *Construye un hallazgo a partir del análisis de la categoría con mayor ingreso.
    @staticmethod
    def build_income_category_finding(result: dict | None) -> dict | None:
        return FindingFunctions._build_category_finding(
            result, "income_category", "Mayor categoría de ingresos", "ingresos"
        )

    # *Construye un hallazgo a partir del análisis de la categoría con mayores ventas.
    @staticmethod
    def build_sales_category_finding(result: dict | None) -> dict | None:
        return FindingFunctions._build_category_finding(
            result, "sales_category", "Mayor categoría de ventas", "ventas"
        )
