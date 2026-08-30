from app.models.users import Users
from app.models.recovery import Recovery
from app.utils.recoveryCode import generar_codigo_recuperacion
from datetime import datetime,timezone
from app.core.security.password import HashPassword as hp

class RecoveryService:
    def __init__(self,repository,repositoryUser):
        self.repository=repository
        self.repositoryUser=repositoryUser
    def request_recovery(self, email):
        user = self.repositoryUser.get_by_email(email)
        if not user:
            raise ValueError("Si el correo está registrado, recibirás un código.")
        # Invalidar recuperaciones anteriores
        #self.repository.invalidate_user_recoveries(user.id)
        # Generar código, token y expiración
        datos = generar_codigo_recuperacion()
        recovery = Recovery(
            user_id=user.user_id,
            codigo=datos["codigo_numerico"],
            token=datos["token_seguro"],
            expires_at=datos["expira_en"]
        )
        # Guardar en BD
        self.repository.create(recovery)
        # Devolver información necesaria para continuar
        return {
            "codigo": datos["codigo_numerico"],
            "email":user.email,
            "user_id":user.user_id
        }
    def verify_recovery_code(self, user_id: int, code: str):
        recovery = self.repository.find_valid_recovery(user_id,code)
        if not recovery:
            raise ValueError("El código no es válido o ha expirado.")
        return recovery
    def reset_password(self, recovery: Recovery, new_password: str):
        # Verificar que la recuperación siga siendo válida
        if recovery.used:
            raise ValueError("Esta recuperación ya fue utilizada.")
        if recovery.expires_at <= datetime.utcnow():
            raise ValueError("Esta recuperación ha expirado.")
        # Generar hash
        password_hash = hp.hash_password(new_password)
        # Buscar usuario
        user = self.repositoryUser.get_by_id(recovery.user_id)
        if not user:
            raise ValueError("El usuario no existe.")
        # Actualizar contraseña
        self.repositoryUser.update_password(user,password_hash)
        # Invalidar recuperación
        self.repository.invalidate_recovery(recovery)
        return True