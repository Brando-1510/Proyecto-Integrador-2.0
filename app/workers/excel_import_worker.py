from PySide6.QtCore import QObject, Signal, Slot
from app.excel_utils.import_service import ImportService
from app.excel_utils.excel_result import ExcelImportResult
class ExcelImportWorker(QObject):
    finished = Signal(ExcelImportResult)
    error = Signal(str)
    progress = Signal(int)
    message = Signal(str)
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.import_service = ImportService()
    @Slot()
    def run(self):
        try:
            result = self.import_service.process_excel(
                self.path,
                progress_callback=self.update_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    @Slot(int, str)
    def update_progress(self, value: int, message: str):
        self.progress.emit(value)
        self.message.emit(message)