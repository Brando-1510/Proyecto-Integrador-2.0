class FindingFunctions:
    #*Formatea un importe para incluirlo en una descripción.
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

    #*Construye un hallazgo a partir del análisis estadístico de la variabilidad de las ventas.
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
