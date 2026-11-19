from app.database.connection import SessionLocal
from app.models.users import Users
from app.models.user_business import Role
from app.core.security.password import HashPassword as hp
from app.core.security.account_validation import normalize_email, validate_registration, validate_new_password
from app.repositories.user_repository import UserRepository
from app.repositories.business_repository import BusinessRepository
from app.repositories.user_business_repository import UserBusinessRepository
from app.utils.validators import ValidadoresDatos
from datetime import date

class UserService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
    def save_user(self, name, email, birthday, password):
        # Valida en servicio: no confiar exclusivamente en validaciones del formulario.
        name, email = validate_registration(name, email, birthday, password)
        with self.session_factory() as session:
            repository = UserRepository(session)
            if repository.email_exists(email):
                raise ValueError("El email que ingresó ya está registrado")
            user = Users(username=name, email=email,
                         password=hp.hash_password(password), birth_date=birthday)
            try:
                created = repository.create(user)
                session.commit()
                session.refresh(created)
                session.expunge(created)
                return created
            except Exception:
                session.rollback()
                raise

    def login_user(self, email, password):
        email = normalize_email(email)
        if not email or not isinstance(password, str) or not password:
            raise ValueError("Las credenciales no son válidas")
        with self.session_factory() as session:
            repository = UserRepository(session)
            user = repository.get_by_email(email)
            if user is None or not hp.verify_password(password, user.password):
                raise ValueError("Las credenciales no son válidas")
            session.expunge(user)
            return user

    def make_admin(self, user_id):
        with self.session_factory() as session:
            repository = UserRepository(session)
            business_repository = BusinessRepository(session)
            user_business_repository = UserBusinessRepository(session)
            try:
                user = repository.get_by_id(user_id)
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
                businesses = business_repository.get_all()
                relationships = []
                for business in businesses:
                    user_business = (
                        user_business_repository.create_relationship(
                            user_id=user.user_id,
                            business_id=business.business_id,
                            role=Role.ADMIN
                        )
                    )
                    relationships.append(user_business)
                session.commit()
                session.refresh(user)
                for relationship in relationships:
                    session.refresh(relationship)
                    session.expunge(relationship)
                session.expunge(user)
                return {
                    "success": True,
                    "user": user,
                    "relationships": relationships
                }
            except Exception as e:
                session.rollback()
                return {
                    "success": False,
                    "message": str(e)
                }
    def save_changes(
        self,user_id:int,username:str | None,email:str | None,fecha: date | None
    ):
        with self.session_factory() as session:
            repository=UserRepository(session)
            if username is None and email is None and fecha is None:
                raise ValueError("No hay cambios para guardar")
            try:
                if email is not None:
                    email = normalize_email(email)
                    if len(email) > 150 or not ValidadoresDatos.validar_correo(email):
                        raise ValueError("El correo electrónico no tiene un formato válido.")
                #*Modificar la informacion del usuario
                user=repository.modify_user(
                    user_id=user_id,
                    username=username,
                    email=email,
                    fecha=fecha
                )
                if user is None:
                    raise ValueError("El usuario no existe.")
                session.commit()
                session.expunge(user)
                return {
                    "success": True,
                    "usuario": user,
                    "message": ("Información actualizada correctamente."),
                }
            except ValueError as e:
                session.rollback()
                return {
                    "success": False,
                    "message": str(e),
                }
            except Exception:
                session.rollback()
                return {
                    "success": False,
                    "message": (
                        "Ocurrió un error al guardar los cambios."
                    ),
                }
    def change_password(self,user_id:int,password:str):
        validate_new_password(password)
        with self.session_factory.begin() as session:
            user_repository = UserRepository(session)
            user = user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("El usuario no existe.")
            password_hash = hp.hash_password(password)
            user_repository.update_password(user,password_hash)
        return True

