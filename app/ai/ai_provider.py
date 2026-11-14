import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_OUTPUT_TOKENS, GEMINI_TIMEOUT
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(handler)


class AIProviderError(Exception):
    """Error general del proveedor de IA."""
class AITimeoutError(AIProviderError):
    """La solicitud superó el tiempo permitido."""
class AIConnectionError(AIProviderError):
    """No se pudo establecer comunicación con Gemini."""
class AIRateLimitError(AIProviderError):
    """Se excedió el límite de solicitudes permitido."""

class AIProvider:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise AIProviderError("No se ha configurado GEMINI_API_KEY.")
        self.model = GEMINI_MODEL
        self.temperature = GEMINI_TEMPERATURE
        self.max_output_tokens = GEMINI_MAX_OUTPUT_TOKENS
        if GEMINI_TIMEOUT <= 0:
            raise ValueError("El timeout debe ser mayor que cero.")
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=GEMINI_TIMEOUT,
                retry_options=types.HttpRetryOptions(
                    attempts=3,initial_delay=1.0,max_delay=5.0,exp_base=2.0,jitter=1.0,http_status_codes=[408, 429, 500, 502, 503, 504]
                )
            )
        )
    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self.max_output_tokens,
                    thinking_config=types.ThinkingConfig(thinking_level="LOW")
                )
            )
            if response.usage_metadata:
                logger.info("Consumo de Gemini: %s", response.usage_metadata)
            if response.candidates:
                finish_reason = response.candidates[0].finish_reason
                logger.info("Finalización de Gemini: %s", finish_reason)
                if finish_reason == types.FinishReason.MAX_TOKENS:
                    raise AIProviderError(
                        "Gemini alcanzó el límite de generación. "
                        "La respuesta podría estar incompleta."
                    )
            if not response.text or not response.text.strip():
                raise AIProviderError("Gemini no generó una respuesta de texto.")
            return response.text.strip()
        except APIError as error:
            self._handle_api_error(error)
        except AIProviderError:
            raise
        except Exception as error:
            error_name = type(error).__name__.lower()
            if "timeout" in error_name or isinstance(error, TimeoutError):
                logger.warning("Tiempo de espera agotado en AIProvider.")
                raise AITimeoutError("AIProvider tardó demasiado en responder.") from error
            if (
                "connect" in error_name
                or "connection" in error_name
                or isinstance(error, ConnectionError)
            ):
                logger.warning("Error de conexión con Gemini.")
                raise AIConnectionError("No se pudo establecer conexión con Gemini.") from error
            logger.exception("Error inesperado en AIProvider.")
            raise AIProviderError("Ocurrió un error al generar el análisis financiero.") from error
    @staticmethod
    def _handle_api_error(error: APIError):
        status_code = getattr(error, "code", None)
        if status_code == 429:
            logger.warning("Límite de solicitudes de Gemini alcanzado.")
            raise AIRateLimitError(
                "Se alcanzó el límite de solicitudes de Gemini. "
                "Intenta nuevamente más tarde."
            ) from error
        if status_code == 408:
            raise AITimeoutError("Gemini tardó demasiado en responder.") from error
        if status_code is not None and status_code >= 500:
            logger.error("Error interno de Gemini: %s", status_code)
            raise AIProviderError("El servicio de Gemini no está disponible temporalmente.") from error
        if status_code in (401, 403):
            raise AIProviderError("No se pudo autenticar la solicitud con Gemini.") from error
        if status_code == 404:
            raise AIProviderError("El modelo de IA configurado no está disponible.") from error
        logger.error("Error de API de Gemini: %s", status_code)
        raise AIProviderError("Gemini no pudo procesar la solicitud.") from error
    def close(self):
        self.client.close()
