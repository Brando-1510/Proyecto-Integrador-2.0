from app.models.users import Users
from app.models.user_business import Role
from app.core.security.password import HashPassword as hp
class UserService:
    def __init__(self,repository,business_repository,user_business_repository):
        self.repository = repository
        self.business_repository = business_repository
        self.user_business_repository = user_business_repository
    def save_user(self, name, email, date, password_hash):
        if self.repository.email_exists(email):
            raise ValueError("El email que ingresó ya está registrado")
        user = Users(
            username=name,
            email=email,
            password=password_hash,
            birth_date=date
        )
        user_created = self.repository.create(user)
        self.repository.session.commit()
        return user_created
    def login_user(self, email, password):
        user = self.repository.get_by_email(email)
        if not user:
            raise ValueError("Las credenciales no son válidas")
        is_correct = hp.verify_password(password,user.password)
        if is_correct:
            return user
        raise ValueError("Las credenciales no son válidas")
    def make_admin(self, user_id):
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "message": "Usuario no encontrado."
                }
            if user.is_admin:
                return {
                    "success": False,
                    "message": "El usuario ya es administrador."
                }
            user.is_admin = True
            businesses = self.business_repository.get_all()
            relationships = []
            for business in businesses:
                user_business = self.user_business_repository.create_relationship(
                    user_id=user.user_id,
                    business_id=business.business_id,
                    role=Role.ADMIN
                )
                relationships.append(user_business)
            self.repository.session.commit()
            return {
                "success": True,
                "user": user,
                "relationships": relationships
            }
        except Exception as e:
            self.repository.session.rollback()
            return {
                "success": False,
                "message": str(e)
            }