class ChooseBusinessController:
    def __init__(self, service):
        self.service = service
    def load_businesses(self, user_id):
        try:
            user_businesses = self.service.get_user_businesses(user_id)
            return {
                "success": True,
                "userBusinesses": user_businesses or []
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            print(
                "ERROR EN load_businesses:",
                type(e).__name__,
                str(e)
            )
            return {
                "success": False,
                "message": "Ocurrió un error al cargar los negocios"
            }