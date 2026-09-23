from datetime import datetime, timezone
from sqlalchemy import select, update
from app.models.recovery import Recovery

class RecoveryRepository:
    def __init__(self, session):
        self.session = session
    def create(self, recovery: Recovery):
        self.session.add(recovery)
        self.session.flush()
        return recovery
    def find_valid_recovery(self, user_id: int, code: str):
        stmt = select(Recovery).where(
            Recovery.user_id == user_id,
            Recovery.code == code,
            Recovery.expires_at > datetime.now(timezone.utc),
            Recovery.used.is_(False)
        )
        return self.session.scalar(stmt)
    def invalidate_recovery(self, recovery: Recovery):
        recovery.used = True
        self.session.flush()
    def invalidate_user_recoveries(self, user_id: int):
        stmt = (
            update(Recovery)
            .where(
                Recovery.user_id == user_id,
                Recovery.used.is_(False)
            )
            .values(used=True)
        )
        self.session.execute(stmt)
        self.session.flush()