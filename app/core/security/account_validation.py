#Reglas de cuenta reutilizables, independientes de los widgets Qt.
import re
from datetime import date, datetime
from calendar import monthrange

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$", re.UNICODE)
NAME_RE = re.compile(r"[^\W\d_]+(?:[ '-][^\W\d_]+)*", re.UNICODE)


def normalize_email(email):
    return (email or "").strip().casefold()


def validate_registration(name, email, birthday, password):
    if not isinstance(name, str) or len(name.strip()) > 150 or not NAME_RE.fullmatch(name.strip()):
        raise ValueError("El nombre solo puede contener letras, espacios, guiones y apóstrofes.")
    if not isinstance(email, str) or len(email.strip()) > 150 or not EMAIL_RE.fullmatch(email.strip()):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    if not isinstance(birthday, date) or isinstance(birthday, datetime):
        raise ValueError("La fecha de nacimiento no es válida.")
    today = date.today()
    year = today.year - 18
    max_day = min(today.day, monthrange(year, today.month)[1])
    age_limit = today.replace(year=year, day=max_day)
    if birthday > age_limit:
        raise ValueError("Debes tener al menos 18 años para crear una cuenta.")
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("La contraseña debe contener al menos 8 caracteres.")
    if not (re.search(r"[A-Z]", password) and re.search(r"[a-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-=\[\]\\/;`~]", password)):
        raise ValueError("La contraseña requiere mayúscula, minúscula, número y carácter especial.")
    return name.strip(), normalize_email(email)


def validate_new_password(password):
    # Las recuperaciones y cambios de contraseña no necesitan validar nombre/fecha.
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("La contraseña debe contener al menos 8 caracteres.")
    if not (re.search(r"[A-Z]", password) and re.search(r"[a-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r"[!@#$%^&*(),.?\":{}|<>_+\-=\[\]\\/;`~]", password)):
        raise ValueError("La contraseña requiere mayúscula, minúscula, número y carácter especial.")
    return True
