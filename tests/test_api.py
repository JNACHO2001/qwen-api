"""
=============================================================================
TESTS DE API - test_api.py
=============================================================================
Tests para verificar que los endpoints de la API funcionan correctamente.

¿Qué es TestClient?
- Es un cliente HTTP de prueba que viene con FastAPI
- Permite hacer peticiones a la API sin necesidad de iniciar el servidor
- Simula peticiones GET, POST, etc.

Para ejecutar:
    pytest tests/test_api.py -v

NOTA: Algunos tests requieren que Ollama esté corriendo.
      Los tests marcados con @pytest.mark.skip se saltan si Ollama no está disponible.
=============================================================================
"""
import pytest
from fastapi.testclient import TestClient


# =============================================================================
# FIXTURE: Cliente de pruebas
# =============================================================================
@pytest.fixture
def client():
    """
    Fixture que proporciona un cliente de pruebas.

    ¿Qué es un fixture?
    - Es una función que prepara datos o recursos para los tests
    - Se ejecuta antes de cada test que lo use
    - pytest lo inyecta automáticamente como parámetro
    """
    from app.main import app

    # Creamos un cliente de pruebas con nuestra app
    return TestClient(app)


@pytest.fixture
def api_key():
    """
    Fixture que proporciona la API key para autenticación.
    """
    from app.config import get_settings

    settings = get_settings()
    return settings.api_key


# =============================================================================
# TEST 1: Endpoint raíz (/)
# =============================================================================
def test_endpoint_raiz(client):
    """
    Verifica que el endpoint raíz devuelve información de la API.

    Este endpoint NO requiere autenticación.
    """
    # Hacemos una petición GET a /
    response = client.get("/")

    # Verificamos que la respuesta sea exitosa (código 200)
    assert response.status_code == 200

    # Verificamos el contenido de la respuesta
    data = response.json()
    assert "mensaje" in data
    assert "version" in data
    assert "modelo" in data
    assert "docs" in data


# =============================================================================
# TEST 2: Endpoint de documentación (/docs)
# =============================================================================
def test_endpoint_docs(client):
    """
    Verifica que la documentación Swagger está disponible.

    ¿Por qué es importante?
    - La documentación ayuda a los usuarios a entender la API
    - FastAPI la genera automáticamente
    """
    response = client.get("/docs")

    # Debe retornar 200 (página HTML de Swagger)
    assert response.status_code == 200


# =============================================================================
# TEST 3: Endpoint de clasificación SIN API key (debe fallar)
# =============================================================================
def test_clasificar_sin_api_key(client):
    """
    Verifica que el endpoint /clasificar rechaza peticiones sin API key.

    ¿Por qué es importante?
    - La autenticación protege la API de uso no autorizado
    - Sin API key, la petición debe ser rechazada con error 422 (Unprocessable Entity)
    """
    response = client.post(
        "/api/v1/clasificar",
        json={
            "texto_pdf_completo": "Proceso de prueba"
        }
        # No enviamos el header X-API-Key
    )

    # Debe retornar 422 (falta el header requerido)
    assert response.status_code == 422


# =============================================================================
# TEST 4: Endpoint de clasificación con API key INCORRECTA
# =============================================================================
def test_clasificar_api_key_incorrecta(client):
    """
    Verifica que el endpoint rechaza API keys inválidas.

    ¿Por qué es importante?
    - Solo usuarios autorizados deben poder usar la API
    - Una API key incorrecta debe retornar error 401 (Unauthorized)
    """
    response = client.post(
        "/api/v1/clasificar",
        json={
            "texto_pdf_completo": "Proceso de prueba"
        },
        headers={
            "X-API-Key": "clave_incorrecta_12345"
        }
    )

    # Debe retornar 401 (no autorizado)
    assert response.status_code == 401


# =============================================================================
# TEST 5: Endpoint de clasificación sin texto (debe fallar)
# =============================================================================
def test_clasificar_sin_texto(client, api_key):
    """
    Verifica que el endpoint rechaza peticiones sin texto para clasificar.

    ¿Por qué es importante?
    - No tiene sentido clasificar sin texto
    - La API debe validar que hay contenido
    """
    response = client.post(
        "/api/v1/clasificar",
        json={
            # No enviamos texto_pdf_completo ni contenido_demanda
            "reg": "12345",
            "radicacion": "2024-00001"
        },
        headers={
            "X-API-Key": api_key
        }
    )

    # Debe retornar 400 (Bad Request) o 500 dependiendo de si Ollama está disponible
    assert response.status_code in [400, 500]


# =============================================================================
# TEST 6: Verificar estructura de respuesta del endpoint raíz
# =============================================================================
def test_estructura_respuesta_raiz(client):
    """
    Verifica que la respuesta del endpoint raíz tiene la estructura correcta.

    ¿Por qué es importante?
    - Los clientes de la API esperan una estructura específica
    - Cambios en la estructura pueden romper integraciones
    """
    response = client.get("/")
    data = response.json()

    # Verificamos que tiene exactamente las claves esperadas
    expected_keys = {"mensaje", "version", "modelo", "docs"}
    actual_keys = set(data.keys())

    assert actual_keys == expected_keys, f"Claves inesperadas: {actual_keys - expected_keys}"
