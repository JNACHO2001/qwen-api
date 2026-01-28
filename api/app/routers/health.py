"""
=============================================================================
ROUTER DE SALUD - health.py
=============================================================================
Proporciona endpoints para verificar el estado del servicio.

Los health checks son esenciales para:
- Monitoreo de infraestructura (Docker, Kubernetes)
- Balanceadores de carga
- Sistemas de alerta y observabilidad
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException  # Router y excepciones HTTP
import ollama  # Cliente para comunicarse con el servidor Ollama
from app.config import get_settings  # Configuración de la aplicación
from app.models import HealthResponse  # Modelo de respuesta

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ROUTER
# -----------------------------------------------------------------------------
router = APIRouter()  # Instancia del router para agrupar endpoints
settings = get_settings()  # Configuración global


# -----------------------------------------------------------------------------
# ENDPOINT DE VERIFICACIÓN DE SALUD
# -----------------------------------------------------------------------------
@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verifica el estado del servicio y conexión con Ollama.
    
    Este endpoint realiza las siguientes verificaciones:
    1. Conexión con el servidor Ollama
    2. Disponibilidad del modelo de IA configurado
    
    Es utilizado por:
    - Docker healthcheck (Dockerfile)
    - docker-compose para dependencias entre servicios
    - Sistemas de monitoreo externos
    
    Returns:
        HealthResponse: Estado del servicio con información de conexión
        
    Raises:
        HTTPException: Error 503 si el servicio no está disponible
    """
    try:
        # Creamos un cliente de Ollama con la URL configurada
        client = ollama.Client(host=settings.ollama_base_url)
        
        # Obtenemos la lista de modelos disponibles en Ollama
        modelos = client.list()
        
        # Verificamos si nuestro modelo configurado está disponible
        # Usamos 'in' para permitir coincidencias parciales (ej: qwen2.5:3b)
        modelo_existe = any(
            settings.model_name in m['name'] 
            for m in modelos.get('models', [])
        )
        
        # Retornamos el estado con toda la información relevante
        return HealthResponse(
            status="healthy" if modelo_existe else "modelo_no_encontrado",
            modelo=settings.model_name,
            ollama_conectado=True,  # Si llegamos aquí, la conexión fue exitosa
            version=settings.app_version
        )
        
    except Exception as e:
        # Si hay cualquier error (conexión, timeout, etc.), retornamos 503
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail=f"Servicio no disponible: {str(e)}"
        )