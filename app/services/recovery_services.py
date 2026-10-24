from app.database.connection import SessionLocal
from app.models.recovery import Recovery
from app.utils.recoveryCode import generar_codigo_recuperacion
from app.core.security.password import HashPassword as hp
from app.repositories.recovery_repository import RecoveryRepository
from app.repositories.user_repository import UserRepository

class RecoveryService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def request_recovery(self, email):
        with self.session_factory.begin() as session:
            recovery_repository = RecoveryRepository(session)
            user_repository = UserRepository(session)
            user = user_repository.get_by_email(email)
            if not user:
                raise ValueError("Si el correo está registrado, recibirás un código.")
            # Invalidar recuperaciones anteriores.
            recovery_repository.invalidate_user_recoveries(user.user_id)
            # Generar código, token y expiración.
            datos = generar_codigo_recuperacion()
            recovery = Recovery(
                user_id=user.user_id,
                code=datos["codigo_numerico"],
                token=datos["token_seguro"],
                expires_at=datos["expira_en"]
            )
            recovery_repository.create(recovery)
            # Preparar los datos antes de cerrar la sesión.
            result = {
                "codigo": datos["codigo_numerico"],
                "email": user.email,
                "user_id": user.user_id
            }
        return result
    def verify_recovery_code(self, user_id: int, code: str):
        with self.session_factory() as session:
            repository = RecoveryRepository(session)
            recovery = repository.find_valid_recovery(user_id,code)
            if not recovery:
                raise ValueError("El código no es válido o ha expirado.")
            session.expunge(recovery)
            return recovery

    def reset_password(self,recovery: Recovery,new_password: str):
        with self.session_factory.begin() as session:
            recovery_repository = RecoveryRepository(session)
            user_repository = UserRepository(session)
            # Volver a consultar la recuperación en esta sesión.
            current_recovery = (
                recovery_repository.find_valid_recovery(recovery.user_id,recovery.code)
            )
            if not current_recovery:
                raise ValueError("El código no es válido o ha expirado, o esta recuperación ya fue utilizada.")
            user = user_repository.get_by_id(current_recovery.user_id)
            if not user:
                raise ValueError("El usuario no existe.")
            password_hash = hp.hash_password(new_password)
            user_repository.update_password(user,password_hash)
            recovery_repository.invalidate_recovery(current_recovery)
        return True
