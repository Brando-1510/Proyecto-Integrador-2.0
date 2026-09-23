from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class SalesTableModel(QAbstractTableModel):
    HEADERS = [
        "Fecha","Descripción","Categoría","Método de pago","Monto",
    ]
    def __init__(self, sales=None):
        super().__init__()
        self.sales = sales or []
    def rowCount(self, parent=QModelIndex()):
        return len(self.sales)
    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section + 1
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        sale = self.sales[index.row()]
        values = [
            sale.date,
            sale.description,
            sale.category,
            sale.payment_method,
            sale.amount,
        ]
        return values[index.column()]
    def set_sales(self, sales):
        self.beginResetModel()
        self.sales = sales or []
        self.endResetModel()