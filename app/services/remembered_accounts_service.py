"""Cuentas recordadas localmente con QSettings + Windows Credential Manager.

No autentica sesiones ni guarda contraseñas en QSettings, archivos o MySQL.
En plataformas no Windows (o backends inseguros) el inicio manual sigue funcionando.
"""
import sys
from dataclasses import dataclass, field
from PySide6.QtCore import QSettings

@dataclass(frozen=True)
class CredentialResult:
    success: bool
    message: str = ""
    secret: str | None = field(default=None, repr=False)

class RememberedAccountsService:
    ORGANIZATION = "Finanzen"
    APPLICATION = "Finanzen"
    SERVICE = "Finanzen.Desktop.Credentials.v1"
    SETTINGS_KEY = "authentication/remembered_emails"

    def __init__(self, settings=None, credential_store=None, strict_backend=True):
        self._settings = settings if settings is not None else QSettings(self.ORGANIZATION, self.APPLICATION)
        self._store = credential_store
        self._strict_backend = strict_backend

    @staticmethod
    def normalize_email(email: str) -> str:
        return (email or "").strip().casefold()

    def _backend(self):
        try:
            if self._store is None:
                import keyring
                provider = keyring
            else:
                provider = self._store
            if self._strict_backend:
                if sys.platform != "win32":
                    return None
                from keyring.backends.Windows import WinVaultKeyring
                if not isinstance(provider.get_keyring(), WinVaultKeyring):
                    return None
            return provider
        except Exception:
            return None

    def available(self) -> bool:
        return self._backend() is not None

    def list_accounts(self) -> list[str]:
        try:
            value = self._settings.value(self.SETTINGS_KEY, [])
            if isinstance(value, str):
                value = [value] if value else []
            if not isinstance(value, (list, tuple)):
                return []
            output = []
            for entry in value:
                email = self.normalize_email(entry) if isinstance(entry, str) else ""
                if email and email not in output:
                    output.append(email)
            return output
        except Exception:
            return []

    def is_remembered(self, email: str) -> bool:
        return self.normalize_email(email) in self.list_accounts()

    def _save_accounts(self, accounts: list[str]) -> bool:
        before = self.list_accounts()
        try:
            self._settings.setValue(self.SETTINGS_KEY, accounts)
            self._settings.sync()
            if self._settings.status() == QSettings.Status.NoError:
                return True
        except Exception:
            pass
        # Restaurar al menos el valor en memoria cuando falla la escritura.
        try:
            self._settings.setValue(self.SETTINGS_KEY, before)
            self._settings.sync()
        except Exception:
            pass
        return False

    def lookup(self, email: str) -> CredentialResult:
        email = self.normalize_email(email)
        if not email or not self.is_remembered(email):
            return CredentialResult(False, "Esta cuenta no está recordada.")
        provider = self._backend()
        if provider is None:
            return CredentialResult(False, "El almacén seguro de Windows no está disponible.")
        try:
            secret = provider.get_password(self.SERVICE, email)
            if secret is None:
                return CredentialResult(False, "No hay contraseña guardada; introdúcela manualmente.")
            return CredentialResult(True, secret=secret)
        except Exception:
            return CredentialResult(False, "No fue posible recuperar la contraseña guardada.")

    def remember(self, email: str, password: str) -> CredentialResult:
        email = self.normalize_email(email)
        if not email or not isinstance(password, str) or not password:
            return CredentialResult(False, "Correo o contraseña no válidos.")
        provider = self._backend()
        if provider is None:
            return CredentialResult(False, "El almacén seguro de Windows no está disponible.")
        previous = self.list_accounts()
        old_password = None
        try:
            old_password = provider.get_password(self.SERVICE, email)
            provider.set_password(self.SERVICE, email, password)
        except Exception:
            return CredentialResult(False, "No fue posible guardar las credenciales en Windows.")
        if self._save_accounts(previous if email in previous else previous + [email]):
            return CredentialResult(True)
        # Revertir la clave, si falla la persistencia de la lista local.
        try:
            if old_password is None:
                provider.delete_password(self.SERVICE, email)
            else:
                provider.set_password(self.SERVICE, email, old_password)
        except Exception:
            pass
        return CredentialResult(False, "No se pudieron guardar las preferencias locales.")

    def forget(self, email: str) -> CredentialResult:
        email = self.normalize_email(email)
        if not email:
            return CredentialResult(False, "Correo inválido.")
        provider = self._backend()
        if provider is None:
            return CredentialResult(False, "El almacén seguro no está disponible para borrar la credencial.")
        previous = self.list_accounts()
        try:
            old_secret = provider.get_password(self.SERVICE, email)
            if old_secret is not None:
                provider.delete_password(self.SERVICE, email)
        except Exception:
            return CredentialResult(False, "No fue posible eliminar la contraseña de Windows.")
        if self._save_accounts([item for item in previous if item != email]):
            return CredentialResult(True)
        # Intentar revertir el borrado, preservando la cuenta anterior.
        if old_secret is not None:
            try:
                provider.set_password(self.SERVICE, email, old_secret)
            except Exception:
                return CredentialResult(False, "Las preferencias no se guardaron y no fue posible restaurar la credencial.")
        return CredentialResult(False, "No se pudieron actualizar las preferencias locales.")

    def update_if_remembered(self, email: str, password: str) -> CredentialResult:
        if not self.is_remembered(email):
            return CredentialResult(True)  # No se ha otorgado consentimiento.
        return self.remember(email, password)

    def rename(self, old_email: str, new_email: str) -> CredentialResult:
        old_email, new_email = self.normalize_email(old_email), self.normalize_email(new_email)
        if old_email == new_email or not self.is_remembered(old_email):
            return CredentialResult(True)
        if self.is_remembered(new_email):
            return CredentialResult(False, "El nuevo correo ya aparece entre las cuentas recordadas.")
        provider = self._backend()
        if provider is None:
            return CredentialResult(False, "El almacén seguro no está disponible.")
        try:
            secret = provider.get_password(self.SERVICE, old_email)
            if secret is not None:
                provider.set_password(self.SERVICE, new_email, secret)
        except Exception:
            return CredentialResult(False, "No se pudo migrar la contraseña almacenada.")
        previous = self.list_accounts()
        replacement = [new_email if x == old_email else x for x in previous]
        if not self._save_accounts(replacement):
            if secret is not None:
                try:
                    provider.delete_password(self.SERVICE, new_email)
                except Exception:
                    pass
            return CredentialResult(False, "No se pudieron migrar las preferencias locales.")
        if secret is not None:
            try:
                provider.delete_password(self.SERVICE, old_email)
            except Exception:
                # Mantener nuevo correo funcional; informar para limpieza manual.
                return CredentialResult(False, "Correo migrado, pero no se pudo borrar la credencial anterior de Windows.")
        return CredentialResult(True)
