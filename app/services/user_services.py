from app.models.users import Users
from app.core.security.password import HashPassword as hp

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
    def login_user(self,email,password):
        user=self.repository.get_by_email(email)
        if not user:
            raise ValueError("Las credenciales no son válidas")
        es_correcto=hp.verify_password(password,user.password)
        if es_correcto:
            return user
        else:
            raise ValueError("Las credenciales no son válidas")