from app.views.login.login import VentanaLogin
from app.views.createAccount.createAccount import VentanaCrearCuenta
from app.views.login.recuperarContra import VentanaRecuperarContra
from app.views.chooseABusiness.chooseABusiness import VentanaChooseBusiness
from app.views.dashboard.dashboard import VentanaDashboard
from app.views.createBusiness.createBusiness import VentanaCreateBusiness

class AppController:
    def __init__(self, container):
        self.container = container
        self.current_user = None
        self.login_window = None
        self.create_account_window = None
        self.recovery_window = None
        self.dashboard_window = None
        self.chooseBusiness_window=None
        self.createBusiness_window=None

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
            self.login_window.login_successful.connect(self.show_choose_business)
        self.login_window.limpiar_campos()
        self.login_window.show()
    #*Crear Cuenta
    def show_create_account(self):
        if self.login_window is not None:
            self.login_window.hide()
        if self.create_account_window is None:
            self.create_account_window = VentanaCrearCuenta(self.container.user_controller)
            self.create_account_window.volver_login_requested.connect(self.show_login)
            self.create_account_window.register_successful.connect(self.show_choose_business)
        self.create_account_window.show()

    #*Recuperar Contraseña
    def show_recovery(self):
        if self.recovery_window is None:
            self.recovery_window = VentanaRecuperarContra(self.container.recovery_controller)
        self.recovery_window.show()

    #*Escoger un negocio
    def show_choose_business(self, user):
        self.current_user = user
        if self.login_window is not None:
            self.login_window.close()
        if self.create_account_window is not None:
            self.create_account_window.close()
        if self.chooseBusiness_window is None:
            self.chooseBusiness_window = VentanaChooseBusiness(
                self.current_user,
                self.container.userBusiness_controller
            )
            self.chooseBusiness_window.dashboard_requested.connect(self.show_dashboard)
            self.chooseBusiness_window.crear_negocio_requested.connect(self.show_create_business)
        self.chooseBusiness_window.show()
    def show_choose_business_again(self):
        if self.createBusiness_window is not None:
            self.createBusiness_window.close()
            self.createBusiness_window = None

        self.show_choose_business(self.current_user)
    # *Mostrar ventana de crear negocio
    def show_create_business(self):
        if self.chooseBusiness_window is not None:
            self.chooseBusiness_window.close()
            self.chooseBusiness_window = None
        self.createBusiness_window = VentanaCreateBusiness(
            self.current_user,
            self.container.business_controller
        )
        self.createBusiness_window.dashboard_requested.connect(self.show_dashboard)
        self.createBusiness_window.volver_choose_business_requested.connect(self.show_choose_business_again)
        self.createBusiness_window.show()
    #*Mostrar Dashboard
    def show_dashboard(self, userBusiness):
        self.dashboard_window = VentanaDashboard(
            userBusiness,self.container.home_dashboard_controller
        )
        self.dashboard_window.logout_requested.connect(self.logout)
        self.dashboard_window.show()
        if self.chooseBusiness_window is not None:
            self.chooseBusiness_window.close()
        if self.createBusiness_window is not None:
            self.createBusiness_window.close()
    def logout(self):
        if self.dashboard_window is not None:
            self.dashboard_window.close()
            self.dashboard_window = None
        if self.chooseBusiness_window is not None:
            self.chooseBusiness_window.close()
            self.chooseBusiness_window = None
        if self.createBusiness_window is not None:
            self.createBusiness_window.close()
            self.createBusiness_window = None
        self.current_user = None
        self.show_login()
    #*Crear Aplicación
    def close(self):
        self.container.close()