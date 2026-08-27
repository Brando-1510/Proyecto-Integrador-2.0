from app.models.users import Users

class UserService:
    def __init__(self, repository):
        self.repository = repository
    def save_user(self, name, email, date, password):
        if self.repository.email_exist(email):
            raise ValueError("El email que ingresó ya está registrado")
        user = Users(
            username=name,
            email=email,
            password=password,
            birth_date=date
        )
        return self.repository.create(user)