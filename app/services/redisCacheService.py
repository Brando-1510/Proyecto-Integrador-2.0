import json
import logging
from datetime import date
import redis
from redis.exceptions import RedisError
from app.config.settings import REDIS_URL
logger = logging.getLogger(__name__)

class RedisCacheService:
    TTL_SECONDS = 86400
    VALID_ANALYSIS_TYPES = (
        "General",
        "Ventas",
        "Ingresos",
        "Gastos"
    )
    def __init__(self):
        self.client = None
        if not REDIS_URL:
            logger.warning("REDIS_URL no está configurada\nLa caché permanecerá deshabilitada.")
            return
        try:
            self.client = redis.Redis.from_url(
                REDIS_URL,
                decode_responses=True,
                protocol=2,
                socket_connect_timeout=2,
                socket_timeout=2
            )
        except (RedisError, ValueError):
            logger.exception("No se pudo inicializar el cliente Redis.")
            self.client = None

    #*Obtener o inicializar la versión del negocio
    def get_version(self, business_id: int) -> int | None:
        if self.client is None:
            return None
        key = f"finanzen:ai:version:{business_id}"
        try:
            # Inicializa únicamente si la clave todavía no existe.
            self.client.set(key, 1, nx=True)
            version = self.client.get(key)
            return int(version) if version is not None else None
        except (RedisError, ValueError):
            logger.exception("No se pudo obtener la versión de caché del negocio %s.",business_id)
            return None

    #*Invalidar la caché de un negocio
    def invalidate_business(self, business_id: int) -> int | None:
        if self.client is None:
            return None
        key = f"finanzen:ai:version:{business_id}"
        try:
            new_version = self.client.incr(key)
            logger.info(
                "Caché invalidada para el negocio %s. Nueva versión: %s",
                business_id,
                new_version
            )
            return new_version
        except RedisError:
            logger.exception("No se pudo invalidar la caché del negocio %s.",business_id)
            return None

    #*Construir la clave de un análisis
    @classmethod
    def _build_analysis_key(
        cls,business_id: int,version: int,analysis_type: str,start_date: date,end_date: date
    ) -> str:
        if analysis_type not in cls.VALID_ANALYSIS_TYPES:
            raise ValueError("Tipo de análisis no válido.")
        return (
            f"finanzen:ai:analysis:{business_id}:"
            f"v{version}:{analysis_type}:"
            f"{start_date.isoformat()}:{end_date.isoformat()}"
        )
    #*Recuperar un análisis almacenado
    def get_analysis(
        self,business_id: int,version: int,analysis_type: str,start_date: date,end_date: date
    ) -> str | None:
        if self.client is None:
            return None
        try:
            key = self._build_analysis_key(business_id,version,analysis_type,start_date,end_date)
            cached_data = self.client.get(key)
            if cached_data is None:
                return None
            response = json.loads(cached_data)
            if not isinstance(response, str):
                logger.warning(
                    "La respuesta almacenada tiene un formato inválido: %s",key
                )
                return None
            logger.info("Análisis recuperado desde Redis: %s", key)
            return response
        except (RedisError, ValueError, TypeError):
            logger.exception("No se pudo recuperar el análisis desde Redis.")
            return None

    #*Almacenar un análisis durante 24 horas
    def set_analysis(
        self,business_id: int,version: int,analysis_type: str,start_date: date,end_date: date,response: str
    ) -> bool:
        if self.client is None:
            return False
        if not isinstance(response, str) or not response.strip():
            return False
        try:
            key = self._build_analysis_key(business_id,version,analysis_type,start_date,end_date)
            serialized_data = json.dumps(response,ensure_ascii=False)
            self.client.set(
                key,serialized_data,ex=self.TTL_SECONDS
            )
            logger.info("Análisis almacenado en Redis: %s", key)
            return True
        except (RedisError, ValueError, TypeError):
            logger.exception("No se pudo almacenar el análisis en Redis.")
            return False

    #*Cerrar conexión Redis
    def close(self):
        if self.client is None:
            return
        try:
            self.client.close()
            logger.info("Conexión Redis cerrada.")
        except RedisError:
            logger.exception("No se pudo cerrar correctamente la conexión Redis.")
