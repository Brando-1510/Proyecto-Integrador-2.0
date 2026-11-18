"""Autorización en servicios de Finanzen basada en la relación usuario-negocio.

No se confía en el rol almacenado en la vista; siempre se consulta MySQL.
La identidad del actor viene del flujo de sesión de la aplicación de escritorio.
"""
from app.models.user_business import Role
from app.repositories.user_business_repository import UserBusinessRepository


class AuthorizationService:
    MANAGERS = frozenset({Role.ADMIN, Role.MANAGER})
    IMPORTERS = frozenset({
        Role.ADMIN,
        Role.MANAGER,
        Role.FINANCIAL_ANALYST,
        Role.EMPLOYEE,
    })
    DENIED = "No tienes autorización para esta operación en el negocio seleccionado."

    @classmethod
    def require_role(cls, session, *, actor_user_id, business_id, allowed_roles):
        # bool es subtipo de int; por eso se utiliza type(...) is int.
        if (type(actor_user_id) is not int or actor_user_id <= 0
                or type(business_id) is not int or business_id <= 0):
            raise PermissionError(cls.DENIED)
        role = UserBusinessRepository(session).get_role(actor_user_id, business_id)
        if role not in allowed_roles:
            raise PermissionError(cls.DENIED)
        return role

    @classmethod
    def require_manage(cls, session, *, actor_user_id, business_id):
        return cls.require_role(
            session,
            actor_user_id=actor_user_id,
            business_id=business_id,
            allowed_roles=cls.MANAGERS,
        )

    @classmethod
    def require_import(cls, session, *, actor_user_id, business_id):
        return cls.require_role(
            session,
            actor_user_id=actor_user_id,
            business_id=business_id,
            allowed_roles=cls.IMPORTERS,
        )
