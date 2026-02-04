"""
=============================================================================
MÓDULO DE MODELOS - models.py
=============================================================================
Define los esquemas de datos (modelos Pydantic) para validar y serializar
las peticiones y respuestas de la API.

Los modelos proporcionan:
- Validación automática de datos de entrada
- Serialización/deserialización JSON
- Documentación automática en Swagger/OpenAPI
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from pydantic import BaseModel, Field  # Clases base y validadores de campos


# -----------------------------------------------------------------------------
# MODELOS DE PETICIÓN (REQUEST)
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    """
    Modelo de respuesta para verificación de salud.

    Proporciona información sobre el estado del servicio y sus dependencias.

    Attributes:
        status: Estado general del servicio ('healthy', 'modelo_no_encontrado', etc.)
        modelo: Nombre del modelo configurado
        ollama_conectado: Indica si hay conexión con el servidor Ollama
        version: Versión actual de la API
    """
    status: str  # Estado del servicio
    modelo: str  # Modelo configurado
    ollama_conectado: bool  # True si Ollama está accesible
    version: str  # Versión de la API


class ProcesoLegalRequest(BaseModel):
    """
    Modelo completo de un proceso legal del Consejo de Estado.
    """

    juzgado_o_tribunal:str = Field(default="")
    juzgado_administrativo:str= Field(default="")
    reg: str = Field(default="")
    radicacion: str = Field(default="")
    ponente: str = Field(default="")
    demandante: str = Field(default="")
    demandado: str = Field(default="")
    clase: str = Field(default="")
    fecha_providencia: str = Field(default="")
    actuacion: str = Field(default="")
    documento: str = Field(default="")
    fecha_estado: str = Field(default="")
    pdf_descargado: bool = Field(default=False)
    ruta_pdf: str = Field(default="")
    texto_pdf_completo: str = Field(default="")
    contenido_demanda: str = Field(default="")


class ProcesoLegalResponse(BaseModel):
    """
    Modelo de respuesta con proceso clasificado.
    """

    juzgado_o_tribunal:str
    juzgado_administrativo:str
    radicacion: str
    ponente: str
    demandante: str
    demandado: str
    clase: str
    fecha_providencia: str
    actuacion: str
    documento: str
    fecha_estado: str
    pdf_descargado: bool
    ruta_pdf: str
    texto_pdf_completo: str
    contenido_demanda: str
    es_relevante: bool
    keywords_encontrados: list = Field(default_factory=list)
    confianza: float
    razon: str
    metodo_clasificacion: str = Field(default="IA")