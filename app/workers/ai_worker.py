import logging
from threading import Event
from PySide6.QtCore import QThread, Signal
from app.services.aiRecommendation_service import AIRecommendationService

from app.ai.ai_provider import AIProvider,AIProviderError,AICancelledError
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
        self.cancel_event = Event()

    def cancelar(self):
        self.cancel_event.set()
        self.requestInterruption()

    def _cancelled(self):
        return (
            self.cancel_event.is_set() or self.isInterruptionRequested()
        )

    def run(self):
        if self._cancelled():
            return
        if self.operation == "analysis":
            self._run_analysis()
        else:
            self._run_assistant()

    def _run_analysis(self):
        provider = None
        try:
            metadata = self.service.get_analysis_metadata(self.datos)
            if self._cancelled():
                return
            business_id = metadata["business_id"]
            version = self.service.get_analysis_version(business_id)
            if self._cancelled():
                return
            if version is not None:
                cached_response = self.service.get_cached_analysis(metadata, version)
                if self._cancelled():
                    return
                if cached_response is not None:
                    logger.info(
                        "Análisis recuperado desde caché. "
                        "Negocio: %s, tipo: %s",
                        business_id,
                        metadata["analysis_type"]
                    )
                    self.result_ready.emit(cached_response)
                    return
            prompt = self.service.prepare_analysis_from_metadata(metadata)
            if self._cancelled():
                return
            provider = AIProvider()
            response = provider.generate(prompt,cancel_event=self.cancel_event)
            if self._cancelled():
                return
            if version is not None:
                self.service.save_cached_analysis(metadata, version, response)
            if not self._cancelled():
                self.result_ready.emit(response)
        except AICancelledError:
            logger.info("Solicitud de análisis cancelada por el usuario.")
        except AIProviderError as error:
            if not self._cancelled():
                logger.warning("Error del proveedor de IA: %s", error)
                self.error_occurred.emit(str(error))
        except ValueError as error:
            if not self._cancelled():
                logger.warning("Datos inválidos para la solicitud: %s", error)
                self.error_occurred.emit(str(error))
        except Exception:
            if not self._cancelled():
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
            if self._cancelled():
                return
            provider = AIProvider()
            response = provider.generate(prompt,cancel_event=self.cancel_event)
            if not self._cancelled():
                self.result_ready.emit(response)
        except AICancelledError:
            logger.info("Solicitud al asistente cancelada por el usuario.")
        except AIProviderError as error:
            if not self._cancelled():
                logger.warning("Error del proveedor de IA: %s", error)
                self.error_occurred.emit(str(error))
        except ValueError as error:
            if not self._cancelled():
                logger.warning("Datos inválidos para la solicitud: %s", error)
                self.error_occurred.emit(str(error))
        except Exception:
            if not self._cancelled():
                logger.exception("Error inesperado durante AIWorker.")
                self.error_occurred.emit("Ocurrió un error inesperado al generar la respuesta del asistente.")
        finally:
            if provider:
                try:
                    provider.close()
                except Exception:
                    logger.exception("No se pudo cerrar el cliente de AIProvider.")
