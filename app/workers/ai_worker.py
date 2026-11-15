import logging
from PySide6.QtCore import QThread, Signal
from app.services.aiRecommendation_service import AIRecommendationService
from app.ai.ai_provider import AIProvider, AIProviderError
logger = logging.getLogger(__name__)

class AIWorker(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)
    def __init__(
        self,service: AIRecommendationService,datos: dict,operation: str,parent=None
    ):
        super().__init__(parent)
        if operation not in ("analysis", "assistant"):
            raise ValueError("Tipo de operación no válido.")
        self.service = service
        self.datos = dict(datos)
        self.operation = operation

    def run(self):
        if self.operation == "analysis":
            self._run_analysis()
        else:
            self._run_assistant()
    def _run_analysis(self):
        provider = None
        try:
            #*Obtener metadatos del análisis.
            metadata = self.service.get_analysis_metadata(self.datos)
            business_id = metadata["business_id"]
            #*Obtener la versión actual de la caché.
            version = self.service.get_analysis_version(business_id)
            #*Consultar si existe un análisis almacenado.
            if version is not None:
                cached_response = self.service.get_cached_analysis(metadata, version)
                if cached_response is not None:
                    logger.info(
                        "Análisis recuperado desde caché. "
                        "Negocio: %s, tipo: %s",
                        business_id,
                        metadata["analysis_type"]
                    )
                    self.result_ready.emit(cached_response)
                    return
            #*Si no existe, preparar el prompt.
            prompt = self.service.prepare_analysis_from_metadata(metadata)
            #*Generar respuesta mediante Gemini.
            provider = AIProvider()
            response = provider.generate(prompt)
            #*Intentar guardar la respuesta en Redis.
            if version is not None:
                self.service.save_cached_analysis(metadata, version, response)
            #*Devolver la respuesta.
            self.result_ready.emit(response)
        except AIProviderError as error:
            logger.warning("Error del proveedor de IA: %s", error)
            self.error_occurred.emit(str(error))
        except ValueError as error:
            logger.warning("Datos inválidos para la solicitud: %s", error)
            self.error_occurred.emit(str(error))
        except Exception:
            logger.exception("Error inesperado durante AIWorker.")
            self.error_occurred.emit("Ocurrió un error inesperado al generar el análisis financiero.")
        finally:
            if provider:
                try:
                    provider.close()
                except Exception:
                    logger.exception("No se pudo cerrar el cliente de AIProvider.")
    def _run_assistant(self):
        provider = None
        try:
            prompt = self.service.prepare_assistant_prompt(self.datos)
            provider = AIProvider()
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
            self.error_occurred.emit(
                "Ocurrió un error inesperado al generar el análisis financiero."
            )
        finally:
            if provider:
                try:
                    provider.close()
                except Exception:
                    logger.exception("No se pudo cerrar el cliente de AIProvider.")
