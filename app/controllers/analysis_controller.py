from app.services.analysis_service import AnalysisService

class AnalysisController:
    def __init__(self, service: AnalysisService):
        self.service = service
    # Ejecuta el análisis financiero del período seleccionado.
    def analyze_period(self, datos: dict) -> dict | None:
        try:
            resultado = self.service.analyze_period(datos)
            return resultado
        except PermissionError as e:
            return{
                "success":False,
                "message":str(e)
            }
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
