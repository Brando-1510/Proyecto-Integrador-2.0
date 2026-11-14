import redis
from app.config.settings import REDIS_URL

def test_redis_connection():
    try:
        # En redis>=5/6/7/8, creamos el cliente directamente desde la URL.
        # Si tu servidor de Redis es antiguo (anterior a la v6), aseguramos el protocolo o conexión básica.
        client = redis.Redis.from_url(
            REDIS_URL, 
            decode_responses=True, 
            db=0,
            protocol=2
        )
        
        # 1. Probar la conexión con ping
        if client.ping():
            print("¡Conexión a Redis establecida correctamente!")
            
            # 2. Escribir un valor de prueba
            client.set('mensaje_prueba', '¡Hola desde Python, Redis funciona con v8.1.0!')
            print("Valor guardado exitosamente en Redis.")
            
            # 3. Leer el valor de prueba
            valor = client.get('mensaje_prueba')
            print(f"Valor recuperado de Redis: '{valor}'")
            
        else:
            print("No se pudo establecer la conexión con Redis.")
            
    except redis.ConnectionError as e:
        print(f"Error: No se pudo conectar al servidor de Redis. Asegúrate de que esté encendido.\nDetalles: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    test_redis_connection()