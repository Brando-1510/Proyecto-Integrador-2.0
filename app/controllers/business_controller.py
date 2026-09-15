class BusinessController:
    def __init__(self, service):
        self.service = service
    def create_business(
        self,user_id,business_name,type_of_business,start_of_operation,description
    ):
        result = self.service.create_business(
            user_id,business_name,type_of_business,start_of_operation,description
        )
        if not result["success"]:
            return {
                "success": False,
                "message": result["message"]
            }
        return {
            "success": True,
            "message": "Negocio creado con éxito",
            "business": result["business"],
            "userBusiness": result["userBusiness"]
        }