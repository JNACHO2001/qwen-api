"""
=============================================================================
TESTS DE MODELOS - test_models.py
=============================================================================
Tests para verificar que los modelos Pydantic funcionan correctamente.

¿Qué son los modelos Pydantic?
- Son clases que definen la estructura de los datos
- Validan automáticamente que los datos sean del tipo correcto
- Convierten JSON a objetos Python y viceversa

Para ejecutar:
    pytest tests/test_models.py -v
=============================================================================
"""
import pytest


# =============================================================================
# TEST 1: Crear un HealthResponse válido
# =============================================================================
def test_health_response_valido():
    """
    Verifica que podemos crear un HealthResponse con datos válidos.

    ¿Por qué es importante?
    - Este modelo se usa en el endpoint /health
    - Si falla, la API no puede reportar su estado
    """
    from app.models import HealthResponse

    # Creamos una respuesta de health check
    response = HealthResponse(
        status="healthy",
        modelo="qwen2.5:3b",
        ollama_conectado=True,
        version="1.0.0"
    )

    # Verificamos que los valores se asignaron correctamente
    assert response.status == "healthy"
    assert response.modelo == "qwen2.5:3b"
    assert response.ollama_conectado is True
    assert response.version == "1.0.0"


# =============================================================================
# TEST 2: Crear un ProcesoLegalRequest con valores mínimos
# =============================================================================
def test_proceso_legal_request_minimo():
    """
    Verifica que podemos crear un ProcesoLegalRequest con datos mínimos.

    ¿Por qué es importante?
    - Los usuarios pueden enviar solo algunos campos
    - Los campos opcionales deben tener valores por defecto
    """
    from app.models import ProcesoLegalRequest

    # Creamos un request con solo el texto necesario para clasificar
    request = ProcesoLegalRequest(
        texto_pdf_completo="Este es un proceso sobre alumbrado público"
    )

    # Verificamos que el campo principal está correcto
    assert "alumbrado" in request.texto_pdf_completo

    # Verificamos que los campos opcionales tienen valores por defecto
    assert request.reg == ""  # Valor por defecto es string vacío
    assert request.radicacion == ""
    assert request.pdf_descargado is False  # Valor por defecto es False


# =============================================================================
# TEST 3: Crear un ProcesoLegalRequest completo
# =============================================================================
def test_proceso_legal_request_completo():
    """
    Verifica que podemos crear un ProcesoLegalRequest con todos los campos.

    ¿Por qué es importante?
    - Asegura que todos los campos funcionan correctamente
    - Documenta la estructura completa del modelo
    """
    from app.models import ProcesoLegalRequest

    # Creamos un request con todos los campos
    request = ProcesoLegalRequest(
        juzgado_o_tribunal="Consejo de Estado",
        juzgado_administrativo="Sección Tercera",
        reg="12345",
        radicacion="2024-00001",
        ponente="Juan Pérez",
        demandante="Empresa ABC",
        demandado="Municipio XYZ",
        clase="Acción de Tutela",
        fecha_providencia="2024-01-15",
        actuacion="Sentencia",
        documento="Auto",
        fecha_estado="2024-01-20",
        pdf_descargado=True,
        ruta_pdf="/documentos/proceso.pdf",
        texto_pdf_completo="Texto del proceso sobre DOLMEN...",
        contenido_demanda="Demanda por servicios de alumbrado"
    )

    # Verificamos algunos campos
    assert request.reg == "12345"
    assert request.radicacion == "2024-00001"
    assert request.pdf_descargado is True
    assert "DOLMEN" in request.texto_pdf_completo


# =============================================================================
# TEST 4: Crear un ProcesoLegalResponse válido
# =============================================================================
def test_proceso_legal_response():
    """
    Verifica que podemos crear un ProcesoLegalResponse con clasificación.

    ¿Por qué es importante?
    - Este es el modelo que devuelve la API después de clasificar
    - Debe incluir todos los campos originales + clasificación
    """
    from app.models import ProcesoLegalResponse

    # Creamos una respuesta con clasificación
    response = ProcesoLegalResponse(
        reg="12345",
        radicacion="2024-00001",
        ponente="",
        demandante="",
        demandado="",
        clase="",
        fecha_providencia="",
        actuacion="",
        documento="",
        fecha_estado="",
        pdf_descargado=False,
        ruta_pdf="",
        texto_pdf_completo="Proceso de alumbrado público",
        contenido_demanda="",
        # Campos de clasificación (lo que agrega la IA)
        es_relevante=True,
        keywords_encontrados=["alumbrado", "público"],
        confianza=0.85,
        razon="Menciona alumbrado público directamente",
        metodo_clasificacion="IA"
    )

    # Verificamos los campos de clasificación
    assert response.es_relevante is True
    assert response.confianza == 0.85
    assert response.metodo_clasificacion == "IA"
    assert "alumbrado" in response.keywords_encontrados


# =============================================================================
# TEST 5: Validación de tipos (Pydantic rechaza datos incorrectos)
# =============================================================================
def test_pydantic_validacion_tipos():
    """
    Verifica que Pydantic rechaza datos con tipos incorrectos.

    ¿Por qué es importante?
    - Previene errores en tiempo de ejecución
    - Asegura que los datos siempre sean del tipo esperado
    """
    from app.models import HealthResponse
    from pydantic import ValidationError

    # Intentamos crear un HealthResponse con tipo incorrecto
    # ollama_conectado debe ser bool, no string
    with pytest.raises(ValidationError):
        HealthResponse(
            status="healthy",
            modelo="qwen2.5:3b",
            ollama_conectado="esto deberia ser True o False",  # ERROR: es string
            version="1.0.0"
        )
