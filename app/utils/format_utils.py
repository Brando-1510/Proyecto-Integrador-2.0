from datetime import date
class FormatUtils:
    MONTHS = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    MONTHS_SHORT = [
        "ene",
        "feb",
        "mar",
        "abr",
        "may",
        "jun",
        "jul",
        "ago",
        "sep",
        "oct",
        "nov",
        "dic",
    ]
    @staticmethod
    def short_date(value: date) -> str:
        return f"{value.day} {FormatUtils.MONTHS_SHORT[value.month - 1]}"
    @staticmethod
    def long_date(value: date) -> str:
        month = FormatUtils.MONTHS[value.month - 1]
        return f"{value.day} de {month} de {value.year}"
    @staticmethod
    def date_range_short(start_date: date, end_date: date) -> str:
        return (
            f"{FormatUtils.short_date(start_date)} - "
            f"{FormatUtils.short_date(end_date)}"
        )
    @staticmethod
    def date_range_long(start_date: date, end_date: date) -> str:
        return (
            f"{FormatUtils.long_date(start_date)} - "
            f"{FormatUtils.long_date(end_date)}"
        )