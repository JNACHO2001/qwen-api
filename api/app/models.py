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
from typing import Literal  # Tipo para valores literales permitidos


# -----------------------------------------------------------------------------
# MODELOS DE PETICIÓN (REQUEST)
# -----------------------------------------------------------------------------
class AnalisisRequest(BaseModel):
    """
    Modelo para peticiones de análisis de texto.
    
    Define la estructura y validación de los datos que el cliente
    debe enviar para solicitar un análisis.
    
    Attributes:
        texto: El texto a analizar (entre 1 y 10,000 caracteres)
        tarea: Tipo de análisis a realizar
        temperatura: Control de creatividad del modelo (0.0 = determinista, 2.0 = muy creativo)
        max_tokens: Número máximo de tokens en la respuesta
    """
    
    # Campo obligatorio con validación de longitud
    texto: str = Field(
        ...,  # Los tres puntos indican que es requerido
        min_length=1,  # Mínimo 1 carácter
        max_length=10000  # Máximo 10,000 caracteres
    )
    
    # Tipo de tarea - solo acepta estos 5 valores literales
    tarea: Literal["analizar", "resumir", "sentimiento", "extraer", "keywords"] = "analizar"
    
    # Parámetros del modelo de IA con rangos válidos
    temperatura: float = Field(
        default=0.7,  # Valor equilibrado entre creatividad y coherencia
        ge=0.0,  # Mayor o igual a 0
        le=2.0   # Menor o igual a 2
    )
    
    max_tokens: int = Field(
        default=512,  # Suficiente para respuestas moderadas
        ge=1,  # Mínimo 1 token
        le=2048  # Máximo 2048 tokens
    )
    
    class Config:
        """Configuración del modelo con ejemplo para documentación."""
        json_schema_extra = {
            "example": {
                "texto": "La inteligencia artificial está transformando el mundo",
                "tarea": "sentimiento",
                "temperatura": 0.7,
                "max_tokens": 512
            }
        }


# -----------------------------------------------------------------------------
# MODELOS DE RESPUESTA (RESPONSE)
# -----------------------------------------------------------------------------
class AnalisisResponse(BaseModel):
    """
    Modelo de respuesta para análisis de texto.
    
    Estructura estandarizada para todas las respuestas de análisis.
    
    Attributes:
        status: Estado de la operación ('success' o 'error')
        tarea: Tipo de tarea que se ejecutó
        resultado: Resultado del análisis generado por el modelo
        modelo: Nombre del modelo de IA utilizado
        tokens_usados: Cantidad de tokens consumidos (opcional)
    """
    status: str  # Estado de la operación
    tarea: str  # Tipo de análisis realizado
    resultado: str  # Texto generado por el modelo
    modelo: str  # Identificador del modelo usado
    tokens_usados: int | None = None  # Métrica de uso (puede ser nulo)


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