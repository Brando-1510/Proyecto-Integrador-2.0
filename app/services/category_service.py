from app.database.connection import SessionLocal
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.utils.category_utils import normalize_category_name

class CategoryService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def get_category_map(self,business_id: int,session=None,) -> dict:
        if session is not None:
            repository = CategoryRepository(session)
            return self._build_category_map(repository, business_id)
        with self.session_factory() as session:
            repository = CategoryRepository(session)
            return self._build_category_map(repository, business_id)

    def _build_category_map(self,repository: CategoryRepository,business_id: int,) -> dict:
        categories = repository.get_by_business(business_id)
        return {
            normalize_category_name(category.name): category
            for category in categories
        }
    def create_missing_categories(self,business_id: int,category_names: list[str],session=None,):
        if session is not None:
            repository = CategoryRepository(session)
            self._create_missing_categories(repository,business_id,category_names,)
            return

        with self.session_factory.begin() as session:
            repository = CategoryRepository(session)
            self._create_missing_categories(repository,business_id,category_names,)

    def _create_missing_categories(
        self,repository: CategoryRepository,business_id: int,category_names: list[str],
    ) -> None:
        category_map = self._build_category_map(repository,business_id,)
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
            repository.create_many(categories_to_create)