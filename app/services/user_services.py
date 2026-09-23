from app.models.users import Users
from app.core.security.password import HashPassword as hp

class UserService:
    def __init__(self, repository):
        self.repository = repository
    def save_user(self, name, email, date, password_hash):
        if self.repository.email_exists(email):
            raise ValueError("El email que ingresó ya está registrado")
        user = Users(
            username=name,
            email=email,
            password=password_hash,
            birth_date=date
        )
        return self.repository.create(user)
    def login_user(self, email, password):
        user = self.repository.get_by_email(email)
        if not user:
            raise ValueError("Las credenciales no son válidas")
        is_correct = hp.verify_password(password,user.password)
        if is_correct:
            return user
        raise ValueError("Las credenciales no son válidas")