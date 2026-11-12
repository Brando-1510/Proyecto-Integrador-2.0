import logging
from PySide6.QtCore import QThread, Signal
from app.services.aiRecommendation_service import AIRecommendationService
from app.ai.ai_provider import GeminiProvider, AIProviderError
logger = logging.getLogger(__name__)

class AIWorker(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)
    def __init__(self,service: AIRecommendationService,datos: dict,operation: str,parent=None):
        super().__init__(parent)
        if operation not in ("analysis", "assistant"):
            raise ValueError("Tipo de operación no válido.")
        self.service = service
        self.datos = dict(datos)
        self.operation = operation

    def run(self):
        provider = None
        try:
            prompt = self._prepare_prompt()
            provider = GeminiProvider()
            response = provider.generate(prompt)
            self.result_ready.emit(response)
        except AIProviderError as error:
            logger.warning("Error del proveedor de IA: %s", error)
            self.error_occurred.emit(str(error))
        except ValueError as error:
            logger.warning("Datos inválidos para la solicitud: %s", error)
            self.error_occurred.emit(str(error))
        except Exception:
            logger.exception("Error inesperado durante AIWorker.")
            self.error_occurred.emit("Ocurrió un error inesperado al generar el análisis.")
        finally:
            if provider:
                try:
                    provider.close()
                except Exception:
                    logger.exception(
                        "No se pudo cerrar el cliente de Gemini."
                    )

    def _prepare_prompt(self) -> str:
        if self.operation == "analysis":
            return self.service.prepare_analysis(self.datos)
        return self.service.prepare_assistant_prompt(self.datos)
