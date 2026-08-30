from sqlalchemy import select
from app.models.users import Users
from app.models.recovery import Recovery
from datetime import datetime,timezone

class RecoveryRepository:
    def __init__(self,session):
        self.session=session
    #*Crear una nueva "recuperacion" en la bd
    def create(self,recovery:Recovery):
        self.session.add(recovery)
        self.session.commit()
        self.session.refresh(recovery)
        return recovery
    #*Buscamos un recovery que coincida tanto el codigo, como el usuario
    def find_valid_recovery(self, user_id: int, code: str):
        stmt = select(Recovery).where(
            Recovery.user_id == user_id,
            Recovery.codigo == code,
            Recovery.expires_at > datetime.utcnow(),
            Recovery.used == False
        )
        return self.session.scalar(stmt)
    #*Luego de que un codigo sea usado, used tiene que ser marcado como True
    def invalidate_recovery(self, recovery: Recovery):
        recovery.used = True
        self.session.commit()
    #*Si el usuario ha enviado varias veces la solicitud de recovery, las invalidamos

