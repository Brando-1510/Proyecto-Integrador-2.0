from app.views.login.login import VentanaLogin
from app.views.createAccount.createAccount import VentanaCrearCuenta
from app.views.login.recuperarContra import VentanaRecuperarContra
# from app.views.dashboard.dashboard import VentanaDashboard

class AppController:
    def __init__(self, container):
        self.container = container
        self.login_window = None
        self.create_account_window = None
        self.recovery_window = None
        self.dashboard_window = None

    def start(self):
        self.show_login()

    #*Login
    def show_login(self):
        if self.create_account_window is not None:
            self.create_account_window.hide()
        if self.login_window is None:
            self.login_window = VentanaLogin(self.container.user_controller)
            self.login_window.crear_cuenta_requested.connect(self.show_create_account)
            self.login_window.recuperar_contrasena_requested.connect(self.show_recovery)
        self.login_window.show()

    #*Crear Cuenta
    def show_create_account(self):
        if self.login_window is not None:
            self.login_window.hide()
        if self.create_account_window is None:
            self.create_account_window = VentanaCrearCuenta(self.container.user_controller)
            self.create_account_window.volver_login_requested.connect(self.show_login)
            self.create_account_window.register_successful.connect(self.show_dashboard)
        self.create_account_window.show()

    #*Recuperar Contraseña
    def show_recovery(self):
        if self.recovery_window is None:
            self.recovery_window = VentanaRecuperarContra(self.container.recovery_controller)
        self.recovery_window.show()

    #*Dashboard
    def show_dashboard(self):
        if self.login_window is not None:
            self.login_window.close()
        if self.create_account_window is not None:
            self.create_account_window.close()
        if self.dashboard_window is None:
            pass
        self.dashboard_window.show()

    #*Crear Aplicación
    def close(self):
        self.container.close()