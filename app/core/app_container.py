from app.database.connection import SessionLocal
# Repositories
from app.repositories.user_repository import UserRepository
from app.repositories.recovery_repository import RecoveryRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.import_repository import ImportRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
# Services
from app.services.user_services import UserService
from app.services.recovery_services import RecoveryService
from app.services.user_business_service import UserBusinessService
from app.services.business_service import BusinessService
from app.services.import_service import ImportService
from app.services.category_service import CategoryService
from app.services.transaction_import_service import TransactionImportService
# Controllers
from app.controllers.user_controller import UserController
from app.controllers.recovery_controller import RecoveryController
from app.controllers.choose_business_controller import ChooseBusinessController
from app.controllers.business_controller import BusinessController

class AppContainer:
    def __init__(self):
        self.session = SessionLocal()
        #*Repositories
        self.category_repository = CategoryRepository(self.session)
        self.userBusiness_repository = UserBusinessRepository(self.session)
        self.user_repository = UserRepository(self.session)
        self.business_repository = BusinessRepository(self.session)
        self.recovery_repository = RecoveryRepository(self.session)
        self.import_repository= ImportRepository(self.session)
        self.sale_repository = SaleRepository(self.session)
        self.movement_repository = MovementRepository(self.session)
        #*UserBusiness
        self.userBusiness_service = UserBusinessService(self.userBusiness_repository)
        self.userBusiness_controller = ChooseBusinessController(self.userBusiness_service)
        #*User
        self.user_service = UserService(
            self.user_repository,self.business_repository,self.userBusiness_repository
        )
        self.user_controller = UserController(self.user_service)
        #*Business
        self.business_service = BusinessService(
            self.business_repository,self.category_repository,self.user_repository,self.userBusiness_repository)
        self.business_controller = BusinessController(self.business_service)
        #*Recovery
        self.recovery_service = RecoveryService(self.recovery_repository,self.user_repository)
        self.recovery_controller = RecoveryController(self.recovery_service)
        #*Imports
        self.import_service=ImportService(self.import_repository)
        #*Categories
        self.category_service=CategoryService(self.category_repository)
        #*Servicio de importación de transacciones
        self.transaction_import_service = TransactionImportService(
        self.session,self.import_service,self.sale_repository,self.movement_repository,self.category_service)
    def close(self):
        self.session.close()