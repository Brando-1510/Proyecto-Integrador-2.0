from app.utils.category_utils import normalize_category_name

class CategoryService:
    def __init__(self, category_repository):
        self.category_repository = category_repository
    def get_category_map(self, business_id: int):
        categories = self.category_repository.get_by_business(business_id)
        return {
            normalize_category_name(category.name): category
            for category in categories
        }