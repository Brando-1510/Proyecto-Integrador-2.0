from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class SalesTableModel(QAbstractTableModel):
    HEADERS = [
        "Fecha",
        "Producto/Servicio",
        "Categoría",
        "Cantidad",
        "Precio Unitario",
        "Total",
    ]
    def __init__(self, sales=None):
        super().__init__()
        self.sales = sales
    #*Filas
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        if self.sales is None:
            return 0
        return len(self.sales)
    #*Columnas
    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    #*Headers
    def headerData(self,section,orientation,role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section + 1
    #*Datos
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if self.sales is None:
            return None
        row = index.row()
        column = index.column()
        sale = self.sales.iloc[row]
        values = [
            sale["Fecha"],
            sale["Producto/Servicio"],
            sale["Categoría"],
            sale["Cantidad"],
            sale["Precio Unitario"],
            sale["Total"],
        ]
        if column >= len(values):
            return None
        value = values[column]
        if value is None:
            return ""
        return str(value)
    #*Actualizar Datos
    def set_data(self, sales):
        self.beginResetModel()
        self.sales = sales
        self.endResetModel()