from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class SalesTableModel(QAbstractTableModel):
    HEADERS = ["Fecha", "Producto/servicio", "Categoría", "Cantidad", "Precio unitario", "Total"]
    def __init__(self, sales=None):
        super().__init__()
        self.sales = sales

    #*Filas
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.sales is None: return 0
        return len(self.sales)

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
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole or self.sales is None: return None
        
        sale = self.sales.iloc[index.row()]
        values = [sale["Fecha"], sale["Producto/Servicio"], sale["Categoría"], sale["Cantidad"], sale["Precio Unitario"], sale["Total"]]
        value = values[index.column()]

        return "" if value is None else str(value)

    # Actualizar datos
    def set_data(self, sales):
        self.beginResetModel()
        self.sales = sales
        self.endResetModel()