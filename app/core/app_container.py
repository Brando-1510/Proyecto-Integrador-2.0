from app.database.connection import SessionLocal

from app.repositories.user_repository import UserRepository
from app.services.user_services import UserService
from app.controllers.user_controller import UserController

from app.repositories.recovery_repository import RecoveryRepository
from app.services.recovery_services import RecoveryService
from app.controllers.recovery_controller import RecoveryController


class AppContainer:
    def __init__(self):
        self.session = SessionLocal()
        # User
        self.user_repository = UserRepository(self.session)
        self.user_service = UserService(self.user_repository)
        self.user_controller = UserController(self.user_service)
        # Recovery
        self.recovery_repository = RecoveryRepository(self.session)
        self.recovery_service = RecoveryService(self.recovery_repository,self.user_repository)
        self.recovery_controller = RecoveryController(self.recovery_service)

    def close(self):
        self.session.close()