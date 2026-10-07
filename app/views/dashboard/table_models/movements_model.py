from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class MovementsTableModel(QAbstractTableModel):
    HEADERS = [
        "Fecha",
        "Tipo",
        "Categoría",
        "Descripción",
        "Método de pago",
        "Monto"
    ]
    def __init__(self, movements=None):
        super().__init__()
        self.movements = movements or []
    #*Filas
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.movements)
    #*Columnas
    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    #*Headers
    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section + 1
    #*Datos
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if (
            not index.isValid()
            or role != Qt.ItemDataRole.DisplayRole
        ):
            return None
        movement = self.movements[index.row()]
        values = [
            movement.date,
            movement.type.value,
            movement.category,
            movement.description,
            movement.payment_method.value
                if movement.payment_method else None,
            movement.amount
        ]
        value = values[index.column()]
        return "" if value is None else str(value)
    #*Actualizar datos
    def set_data(self, movements):
        self.beginResetModel()
        self.movements = movements or []
        self.endResetModel()