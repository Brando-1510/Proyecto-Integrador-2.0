from datetime import date, timedelta

class DateUtils:
    @staticmethod
    def last_30_days(end_date: date | None = None) -> tuple[date, date]:
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=29)
        return start_date, end_date
    @staticmethod
    def this_week(end_date:date | None=None) -> tuple[date,date]:
        if end_date is None:
            end_date=date.today()
        start_date=end_date-timedelta(days=end_date.weekday())
        return start_date,end_date
    @staticmethod
    def this_month(end_date: date | None = None) -> tuple[date, date]:
        if end_date is None:
            end_date = date.today()
        start_date = end_date.replace(day=1)
        return start_date, end_date
    @staticmethod
    def last_15_days(end_date: date | None = None) -> tuple[date, date]:
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=14)
        return start_date, end_date
    @staticmethod
    def last_3_months(end_date: date | None = None) -> tuple[date, date]:
            if end_date is None:
                end_date = date.today()
            month = end_date.month - 3
            year = end_date.year
            if month <= 0:
                month += 12
                year -= 1
            try:
                start_date = end_date.replace(year=year, month=month)
            except ValueError:
                from calendar import monthrange
                last_day = monthrange(year, month)[1]
                start_date = end_date.replace(year=year, month=month, day=last_day)
            return start_date, end_date
    @staticmethod
    def last_year(end_date: date | None = None) -> tuple[date, date]:
            if end_date is None:
                end_date = date.today()
            try:
                start_date = end_date.replace(year=end_date.year - 1)
            except ValueError:
                start_date = end_date.replace(year=end_date.year - 1, day=28)
            return start_date, end_date
    @staticmethod
    def previous_month(reference_date: date | None = None) -> tuple[date, date]:
        if reference_date is None:
            reference_date = date.today()
        first_day_current_month = reference_date.replace(day=1)
        end_date = first_day_current_month.fromordinal(
            first_day_current_month.toordinal() - 1
        )
        start_date = end_date.replace(day=1)
        return start_date, end_date