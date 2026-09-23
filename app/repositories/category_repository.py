from sqlalchemy import select
from app.models.category import Category

class CategoryRepository:
    def __init__(self, session):
        self.session = session
    def create(self, category: Category):
        self.session.add(category)
        self.session.flush()
        return category
    def create_many(self, categories: list[Category]):
        self.session.add_all(categories)
        self.session.flush()
        return categories
    def get_by_business(self, business_id: int):
        stmt = (
            select(Category)
            .where(Category.business_id == business_id)
            .order_by(Category.name)
        )
        return self.session.scalars(stmt).all()