from datetime import date, timedelta

class DateUtils:
    @staticmethod
    def last_30_days(end_date: date | None = None) -> tuple[date, date]:
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=29)
        return start_date, end_date