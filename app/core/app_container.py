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
        #*UserBusiness
        self.userBusiness_service = UserBusinessService()
        self.userBusiness_controller = ChooseBusinessController(self.userBusiness_service)

        #*User
        self.user_service = UserService()
        self.user_controller = UserController(self.user_service)

        #*Business
        self.business_service = BusinessService()
        self.business_controller = BusinessController(self.business_service)

        #*Recovery
        self.recovery_service = RecoveryService()
        self.recovery_controller = RecoveryController(self.recovery_service)

        #*Importación de Excel
        self.import_service = ImportService()
        self.category_service = CategoryService()

        self.transaction_import_service = TransactionImportService(
            import_service=self.import_service,category_service=self.category_service,
        )

        #*Home Dashboard
        self.home_dashboard_service = HomeDashboardService()
        self.home_dashboard_controller = HomeDashboardController(self.home_dashboard_service)

        #*Consultation
        self.consultation_service = ConsultationService()
        self.consultation_controller = ConsultationController(self.consultation_service)

        #*Analysis
        self.analysis_service = AnalysisService()
        self.analysis_controller = AnalysisController(self.analysis_service)

        #*Recommendations
        self.recommendation_service = RecommendationService()
        self.recommendation_controller = RecommendationController(self.recommendation_service)

        #*Configuration
        self.configuration_service = ConfigurationService()
        self.configuration_controller = ConfigurationController(self.configuration_service)

        #*Monitoring
        self.monitoring_service = MonitoringService()
        self.monitoring_controller = MonitoringController(self.monitoring_service)
