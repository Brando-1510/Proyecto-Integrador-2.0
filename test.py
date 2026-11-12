from dotenv import load_dotenv

from app.ai.ai_provider import (
    GeminiProvider,
    AIProviderError,
    AITimeoutError,
    AIConnectionError,
    AIRateLimitError
)


load_dotenv()


def main():
    provider = None

    try:
        provider = GeminiProvider()

        response = provider.generate(
            "Explica brevemente la importancia "
            "de controlar los gastos de un negocio."
        )

        print("\nRespuesta de Gemini:\n")
        print(response)

    except AITimeoutError as error:
        print(f"Timeout: {error}")

    except AIConnectionError as error:
        print(f"Conexión: {error}")

    except AIRateLimitError as error:
        print(f"Límite de solicitudes: {error}")

    except AIProviderError as error:
        print(f"Error del proveedor: {error}")

    finally:
        if provider:
            provider.close()


if __name__ == "__main__":
    main()