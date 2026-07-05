from PyQt5.QtCore import QDate


def previous_month_range():
    """Return (first_day, last_day) of the calendar month before today."""
    first_of_this_month = QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)
    last_of_prev_month = first_of_this_month.addDays(-1)
    first_of_prev_month = QDate(last_of_prev_month.year(), last_of_prev_month.month(), 1)
    return first_of_prev_month, last_of_prev_month
