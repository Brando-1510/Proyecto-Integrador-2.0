class UserBusinessService:
    def __init__(self, repository):
        self.repository = repository
    def get_user_businesses(self, user_id: int):
        result=self.repository.get_businesses_by_user(user_id)
        return result