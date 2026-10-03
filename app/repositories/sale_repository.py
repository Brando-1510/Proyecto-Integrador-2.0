from app.models.sale import Sale

class SaleRepository:
    def __init__(self, session):
        self.session = session
    def create(self, sale: Sale):
        self.session.add(sale)
        self.session.flush()
        return sale
    def create_many(self, sales: list[Sale]):
        self.session.add_all(sales)
        self.session.flush()
        return sales