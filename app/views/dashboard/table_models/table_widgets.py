from enum import Enum
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

def populate_table(table: QTableWidget, data: list):
    table.setRowCount(0)
    for row_index, row_data in enumerate(data):
        table.insertRow(row_index)
        for col_index, value in enumerate(row_data):
            if isinstance(value, Enum):
                value = value.value
            item = QTableWidgetItem(str(value))
            table.setItem(row_index, col_index, item)