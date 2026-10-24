from app.database.connection import SessionLocal
# *Repositories
from app.repositories.user_repository import UserRepository
from app.repositories.recovery_repository import RecoveryRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.import_repository import ImportRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.movement_repository import MovementRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.configuration_repository import ConfigurationRepository
from app.repositories.monitoring_repository import MonitoringRepository
#*Services
from app.services.user_services import UserService
from app.services.recovery_services import RecoveryService
from app.services.user_business_service import UserBusinessService
from app.services.business_service import BusinessService
from app.services.import_service import ImportService
from app.services.category_service import CategoryService
from app.services.transaction_import_service import TransactionImportService
from app.services.home_dashboard_service import HomeDashboardService
from app.services.consultation_service import ConsultationService
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService
from app.services.configuration_service import ConfigurationService
from app.services.monitoring_service import MonitoringService
#*Controllers
from app.controllers.user_controller import UserController
from app.controllers.recovery_controller import RecoveryController
from app.controllers.choose_business_controller import ChooseBusinessController
from app.controllers.business_controller import BusinessController
from app.controllers.home_dashboard_controller import HomeDashboardController
from app.controllers.consultation_controller import ConsultationController
from app.controllers.analysis_controller import AnalysisController
from app.controllers.recommendation_controller import RecommendationController
from app.controllers.configuration_controller import ConfigurationController
from app.controllers.monitoring_controller import MonitoringController

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
        self.analysis_repository=AnalysisRepository(self.session)
        self.recommendation_repository=RecommendationRepository(self.session)
        self.configuration_repository=ConfigurationRepository(self.session)
        self.monitoring_repository=MonitoringRepository(self.session)
        #*UserBusiness
        self.userBusiness_service = UserBusinessService(session_factory=SessionLocal)
        self.userBusiness_controller = ChooseBusinessController(self.userBusiness_service)
        #*User
        self.user_service = UserService(session_factory=SessionLocal)
        self.user_controller = UserController(self.user_service)
        #*Business
        self.business_service = BusinessService(session_factory=SessionLocal)
        self.business_controller = BusinessController(self.business_service)
        #*Recovery
        self.recovery_service = RecoveryService(session_factory=SessionLocal)
        self.recovery_controller = RecoveryController(self.recovery_service)
        #*Imports
        self.import_service=ImportService(self.import_repository)
        #*Categories
        self.category_service=CategoryService(self.category_repository)
        #*Servicio de importación de transacciones
        self.transaction_import_service = TransactionImportService(
        self.session,self.import_service,self.sale_repository,self.movement_repository,self.category_service)
        #*Home Dashboard
        self.home_dashboard_service=HomeDashboardService()
        self.home_dashboard_controller=HomeDashboardController(self.home_dashboard_service)
        #*Consultation Controlller
        self.consultation_service=ConsultationService()
        self.consultation_controller=ConsultationController(self.consultation_service)
        #*Analysis
        self.analysis_service=AnalysisService()
        self.analysis_controller=AnalysisController(self.analysis_service)
        #*Recommendations
        self.recommendation_service=RecommendationService()
        self.recommendation_controller=RecommendationController(self.recommendation_service)
        #*Configuracion
        self.configuration_service=ConfigurationService()
        self.configuration_controller=ConfigurationController(self.configuration_service)
        #*Monitoreo
        self.monitoring_service=MonitoringService(self.monitoring_repository)
        self.monitoring_controller=MonitoringController(self.monitoring_service)
    def close(self):
        self.session.close()