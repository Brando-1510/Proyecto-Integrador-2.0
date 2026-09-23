from datetime import datetime, timezone
from app.models.recovery import Recovery
from app.utils.recoveryCode import generar_codigo_recuperacion
from app.core.security.password import HashPassword as hp

class RecoveryService:
    def __init__(self, repository, repository_user):
        self.repository = repository
        self.repository_user = repository_user
    def request_recovery(self, email):
        user = self.repository_user.get_by_email(email)
        if not user:
            raise ValueError("Si el correo está registrado, recibirás un código.")
        # Invalidar recuperaciones anteriores
        self.repository.invalidate_user_recoveries(user.user_id)
        # Generar código, token y expiración
        datos = generar_codigo_recuperacion()
        recovery = Recovery(
            user_id=user.user_id,
            code=datos["codigo_numerico"],
            token=datos["token_seguro"],
            expires_at=datos["expira_en"]
        )
        self.repository.create(recovery)
        self.repository.session.commit()
        return {
            "codigo": datos["codigo_numerico"],
            "email": user.email,
            "user_id": user.user_id
        }
    def verify_recovery_code(self, user_id: int, code: str):
        recovery = self.repository.find_valid_recovery(user_id,code)
        if not recovery:
            raise ValueError("El código no es válido o ha expirado.")
        return recovery
    def reset_password(self,recovery: Recovery,new_password: str):
        try:
            if recovery.used:
                raise ValueError("Esta recuperación ya fue utilizada.")
            if recovery.expires_at <= datetime.now(timezone.utc):
                raise ValueError("Esta recuperación ha expirado.")
            password_hash = hp.hash_password(new_password)
            user = self.repository_user.get_by_id(recovery.user_id)
            if not user:
                raise ValueError("El usuario no existe.")
            self.repository_user.update_password(user,password_hash)
            self.repository.invalidate_recovery(recovery)
            self.repository.session.commit()
            return True
        except Exception:
            self.repository.session.rollback()
            raise