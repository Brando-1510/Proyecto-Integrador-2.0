from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_password_hasher = PasswordHasher()

class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        #*Genera un hash seguro para una contraseña.
        return _password_hasher.hash(password)
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        #*Verifica si una contraseña coincide con su hash.
        try:
            return _password_hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False