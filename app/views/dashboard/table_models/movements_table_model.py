from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class MovementsTableModel(QAbstractTableModel):
    HEADERS = [
        "Fecha","Tipo","Categoría","Descripción","Método de pago","Monto",
    ]
    def __init__(self, movements=None):
        super().__init__()
        self.movements = movements or []
    def rowCount(self, parent=QModelIndex()):
        return len(self.movements)
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
        movement = self.movements[index.row()]
        values = [
            movement.date,
            movement.type,
            movement.category,
            movement.description,
            movement.payment_method,
            movement.amount,
        ]
        return values[index.column()]
    def set_movements(self, movements):
        self.beginResetModel()
        self.movements = movements or []
        self.endResetModel()