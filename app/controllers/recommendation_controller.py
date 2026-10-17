from app.services.recommendation_service import RecommendationService

class RecommendationController:
    def __init__(self,service:RecommendationService):
        self.service=service
    def get_recommendations(self,datos):
        try:
            resultado=self.service.generar_recomendaciones(datos)
            return resultado
        except ValueError as e:
            return{
                "success":False,
                "message":str(e)
            }
        except Exception:
            import traceback
            traceback.print_exc()
            return{
                "success":False,
                "message":"Ocurrio un error al cargar los datos"
            }