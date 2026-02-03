"""
=============================================================================
MÓDULO PRINCIPAL DE LA API - main.py
=============================================================================
Punto de entrada de la aplicación FastAPI para análisis de texto con IA.

Este módulo configura:
- La instancia principal de FastAPI con metadatos
- Middleware CORS para peticiones cross-origin
- Registro de routers para organizar los endpoints
- Endpoint raíz informativo

Autor: Proyecto qwen-api
Versión: 1.0.0
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
import logging  # Módulo estándar de Python para logging
from fastapi import FastAPI  # Framework principal para crear la API
from fastapi.middleware.cors import CORSMiddleware  # Middleware para CORS
from app.config import get_settings  # Función para obtener configuración
from app.routers import health, analisis  # Routers de la aplicación

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# -----------------------------------------------------------------------------
# Configuramos el logging para toda la aplicación
# Formato: [FECHA HORA] - NIVEL - NOMBRE_MODULO - MENSAJE
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo de mensajes a mostrar
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Creamos un logger específico para este módulo
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
# -----------------------------------------------------------------------------
# Obtenemos la configuración global de la aplicación (singleton con caché)
settings = get_settings()

# -----------------------------------------------------------------------------
# INSTANCIA DE LA APLICACIÓN FASTAPI
# -----------------------------------------------------------------------------
# Creamos la aplicación con metadatos que aparecerán en la documentación
app = FastAPI(
    title=settings.app_name,  # Nombre de la API
    description="API profesional para análisis de texto usando Qwen 2.5",
    version=settings.app_version,  # Versión de la API
    docs_url="/docs",  # URL de la documentación Swagger UI
    redoc_url="/redoc"  # URL de la documentación alternativa ReDoc
)

# Log de inicio de la aplicación
logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
logger.info(f"Modelo configurado: {settings.model_name}")
logger.info(f"Ollama URL: {settings.ollama_base_url}")

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE CORS (Cross-Origin Resource Sharing)
# -----------------------------------------------------------------------------
# NOTA DE PRODUCCIÓN: En producción, cambiar allow_origins por dominios específicos
# Ejemplo: allow_origins=["https://miapp.com", "https://api.miapp.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ADVERTENCIA: Permite cualquier origen (solo para desarrollo)
    allow_credentials=True,  # Permite cookies y headers de autenticación
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# -----------------------------------------------------------------------------
# REGISTRO DE ROUTERS
# -----------------------------------------------------------------------------
# Los routers organizan los endpoints en grupos lógicos
app.include_router(health.router)  # Endpoints de salud (sin prefijo, /health)
app.include_router(analisis.router, prefix="/api/v1")  # Endpoints de análisis con versionado


# -----------------------------------------------------------------------------
# ENDPOINT RAÍZ
# -----------------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de bienvenida.
    
    Proporciona información básica sobre la API incluyendo:
    - Mensaje de bienvenida
    - Versión actual
    - Modelo de IA configurado
    - Enlace a la documentación
    
    Returns:
        dict: Información básica de la API en formato JSON
    """
    return {
        "mensaje": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "modelo": settings.model_name,
        "docs": "/docs"
    }