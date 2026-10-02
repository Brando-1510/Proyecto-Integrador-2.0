from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class MovementsTableModel(QAbstractTableModel):
    HEADERS = ["Fecha", "Tipo", "Categoría", "Descripción", "Método de pago", "Monto"]

    def __init__(self, movements=None):
        super().__init__()
        self.movements = movements

    #*Filas
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.movements is None: return 0
        return len(self.movements)

    #*Columnas
    def columnCount(self, parent=QModelIndex()):
        if parent.isValid(): return 0
        return len(self.HEADERS)

    #*Headers
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole: return None
        if orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
        return section + 1

    #*Datos
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole or self.movements is None: return None
        movement = self.movements.iloc[index.row()]
        values = [movement["Fecha"], movement["Tipo"], movement["Categoría"], movement["Descripción"], movement["Método de Pago"], movement["Monto"]]
        value = values[index.column()]
        return "" if value is None else str(value)

    #*Actualizar datos
    def set_data(self, movements):
        self.beginResetModel()
        self.movements = movements
        self.endResetModel()