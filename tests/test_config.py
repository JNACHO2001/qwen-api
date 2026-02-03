"""
=============================================================================
TESTS DE CONFIGURACIÓN - test_config.py
=============================================================================
Tests sencillos para verificar que la configuración funciona correctamente.

Para ejecutar estos tests:
    pytest tests/test_config.py -v

Explicación:
- pytest: es el framework de testing que usamos
- -v: modo verbose (muestra más detalles)
=============================================================================
"""
import pytest
import os


# =============================================================================
# TEST 1: Verificar que las variables de entorno se cargan
# =============================================================================
def test_api_key_existe():
    """
    Verifica que la variable API_KEY existe en el entorno.

    ¿Por qué es importante?
    - Sin API_KEY la aplicación no puede autenticar peticiones
    - Este test falla si olvidaste crear el archivo .env
    """
    # Importamos la configuración
    from app.config import get_settings

    # Obtenemos la instancia de settings
    settings = get_settings()

    # Verificamos que api_key no esté vacía
    # assert = "afirmar" - si es False, el test falla
    assert settings.api_key is not None, "API_KEY no está configurada"
    assert len(settings.api_key) > 0, "API_KEY está vacía"


# =============================================================================
# TEST 2: Verificar valores por defecto
# =============================================================================
def test_valores_por_defecto():
    """
    Verifica que los valores por defecto están correctamente configurados.

    ¿Por qué es importante?
    - Asegura que la app funcione incluso sin todas las variables
    - Documenta cuáles son los valores esperados
    """
    from app.config import get_settings

    settings = get_settings()

    # Verificamos los puertos por defecto
    assert settings.api_port == 8000, "Puerto de API debería ser 8000"
    assert settings.ollama_port == 11434, "Puerto de Ollama debería ser 11434"

    # Verificamos que hay un nombre de modelo configurado
    assert settings.model_name is not None, "MODEL_NAME no está configurado"
    assert "qwen" in settings.model_name.lower(), "El modelo debería ser Qwen"


# =============================================================================
# TEST 3: Verificar que ollama_base_url se construye correctamente
# =============================================================================
def test_ollama_base_url():
    """
    Verifica que la URL de Ollama se construye correctamente.

    ¿Por qué es importante?
    - La API necesita conectarse a Ollama
    - Si la URL está mal formada, la conexión fallará
    """
    from app.config import get_settings

    settings = get_settings()

    # La URL debe empezar con http://
    assert settings.ollama_base_url.startswith("http://"), "URL debe empezar con http://"

    # La URL debe contener el puerto
    assert str(settings.ollama_port) in settings.ollama_base_url, "URL debe contener el puerto"


# =============================================================================
# TEST 4: Verificar patrón Singleton
# =============================================================================
def test_singleton_settings():
    """
    Verifica que get_settings() siempre devuelve la misma instancia.

    ¿Qué es el patrón Singleton?
    - Es un patrón que garantiza que solo existe UNA instancia de un objeto
    - Útil para configuración: no queremos leer .env múltiples veces

    ¿Por qué es importante?
    - Mejora el rendimiento (no relee el archivo .env)
    - Garantiza consistencia (todos usan la misma config)
    """
    from app.config import get_settings

    # Obtenemos la configuración dos veces
    settings1 = get_settings()
    settings2 = get_settings()

    # Ambas deben ser EXACTAMENTE el mismo objeto en memoria
    # 'is' compara identidad (mismo objeto), no igualdad (mismo valor)
    assert settings1 is settings2, "get_settings() debe devolver la misma instancia (Singleton)"
