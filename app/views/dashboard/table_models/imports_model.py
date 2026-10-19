from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

class ImportsTableModel(QAbstractTableModel):
    HEADERS = [
        "ID",
        "Nombre del archivo",
        "Fecha de importación",
        "Usuario"
    ]
    def __init__(self, imports=None):
        super().__init__()
        self.imports = imports or []
    #*Filas
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.imports)
    #*Columnas
    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    #*Encabezados
    def headerData(self,section,orientation,role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section + 1
    #*Datos
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if (not index.isValid()or role != Qt.ItemDataRole.DisplayRole):
            return None
        imported = self.imports[index.row()]
        values = [
            imported.import_id,
            imported.file_name,
            imported.imported_at,
            imported.username
        ]
        value = values[index.column()]
        return "" if value is None else str(value)
    #*Actualizar datos
    def set_data(self, imports):
        self.beginResetModel()
        self.imports = imports or []
        self.endResetModel()
