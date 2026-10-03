from app.models.movement import Movement

class MovementRepository:
    def __init__(self, session):
        self.session = session
    def create(self, movement: Movement):
        self.session.add(movement)
        self.session.flush()
        return movement
    def create_many(self, movements: list[Movement]):
        self.session.add_all(movements)
        self.session.flush()
        return movements