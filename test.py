from datetime import date
from app.services.redisCacheService import RedisCacheService

cache = RedisCacheService()

business_id = 999999

# 1. Obtener versión inicial
version = cache.get_version(business_id)
print("Versión inicial:", version)

# 2. Incrementar versión
new_version = cache.invalidate_business(business_id)
print("Nueva versión:", new_version)

# 3. Guardar análisis
saved = cache.set_analysis(
    business_id=business_id,
    version=new_version,
    analysis_type="General",
    start_date=date(2026, 10, 1),
    end_date=date(2026, 10, 31),
    response="Este es un análisis financiero de prueba."
)

print("Guardado:", saved)

# 4. Recuperar análisis
result = cache.get_analysis(
    business_id=business_id,
    version=new_version,
    analysis_type="General",
    start_date=date(2026, 10, 1),
    end_date=date(2026, 10, 31)
)

print("Resultado:", result)

cache.close()