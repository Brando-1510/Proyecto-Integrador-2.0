from PySide6.QtCore import QObject, Signal, Slot
from app.database.connection import SessionLocal
from app.repositories.import_repository import ImportRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.category_repository import CategoryRepository
from app.services.import_service import ImportService
from app.services.category_service import CategoryService
from app.services.transaction_import_service import TransactionImportService
from app.errors.import_errors import (ImportErrorResult,ImportErrorType,)

class ExcelSaveWorker(QObject):
    finished = Signal()
    error = Signal(object)
    progress = Signal(int)
    message = Signal(str)
    def __init__(self,user_id: int,business_id: int,file_path: str,file_name: str,df_sales,df_movements):
        super().__init__()
        self.user_id = user_id
        self.business_id = business_id
        self.file_path = file_path
        self.file_name = file_name
        self.df_sales = df_sales
        self.df_movements = df_movements
    @Slot()
    def run(self):
        session = SessionLocal()
        try:
            self.message.emit("Preparando la importación...")
            self.progress.emit(10)
            import_repository = ImportRepository(session)
            category_repository = CategoryRepository(session)
            sale_repository = SaleRepository(session)
            movement_repository = MovementRepository(session)
            # Services de ESTA sesión
            import_service = ImportService(import_repository)
            category_service = CategoryService(category_repository)
            transaction_service = TransactionImportService(
                session=session,
                import_service=import_service,
                sale_repository=sale_repository,
                movement_repository=movement_repository,
                category_service=category_service
            )
            self.message.emit("Guardando datos...")
            self.progress.emit(20)
            transaction_service.save_import_data(
                user_id=self.user_id,
                business_id=self.business_id,
                file_path=self.file_path,
                file_name=self.file_name,
                df_sales=self.df_sales,
                df_movements=self.df_movements
            )
            self.progress.emit(100)

            self.message.emit("Datos guardados correctamente.")
            self.finished.emit()
        except ValueError as e:
            self.error.emit(
                ImportErrorResult(
                    error_type=ImportErrorType.INVALID_DATA,
                    message=str(e),
                    technical_message=str(e)
                )
            )
        except Exception as e:
            error_message = str(e)
            if "ya existe en la base de datos" in error_message:
                self.error.emit(
                    ImportErrorResult(
                        error_type=ImportErrorType.FILE_ALREADY_EXISTS,
                        message=(
                            "Este archivo ya fue importado "
                            "anteriormente para este negocio."
                        ),
                        technical_message=error_message
                    )
                )
            elif "no existe para este negocio" in error_message:
                self.error.emit(
                    ImportErrorResult(
                        error_type=ImportErrorType.CATEGORY_NOT_FOUND,
                        message=error_message,
                        technical_message=error_message
                    )
                )
            else:
                self.error.emit(
                    ImportErrorResult(
                        error_type=ImportErrorType.DATABASE_ERROR,
                        message=(
                            "No fue posible guardar los datos."
                        ),
                        technical_message=error_message
                    )
                )
        finally:
            session.close()