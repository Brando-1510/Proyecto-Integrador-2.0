from app.models.category import Category
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
    def create_missing_categories(self,business_id: int,category_names: list[str],) -> None:
        category_map = self.get_category_map(business_id)
        categories_to_create = []
        names_seen = set()
        for name in category_names:
            normalized_name = normalize_category_name(name)
            if not normalized_name or normalized_name in names_seen:
                continue
            names_seen.add(normalized_name)
            if normalized_name in category_map:
                continue
            categories_to_create.append(
                Category(
                    business_id=business_id,
                    name=name.strip(),
                    is_system=False,
                )
            )
        if categories_to_create:
            self.category_repository.create_many(categories_to_create)