"""
=============================================================================
MÓDULO DE CONFIGURACIÓN - config.py
=============================================================================
Gestiona toda la configuración de la aplicación usando Pydantic Settings.

Las variables de entorno se cargan automáticamente desde:
1. Variables de entorno del sistema
2. Archivo .env en la raíz del proyecto

Características:
- Validación automática de tipos
- Valores por defecto configurables
- Patrón Singleton con caché (lru_cache)
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from pydantic_settings import BaseSettings  # Clase base para configuración con validación
from functools import lru_cache  # Decorador para caché de función (singleton)


# -----------------------------------------------------------------------------
# CLASE DE CONFIGURACIÓN
# -----------------------------------------------------------------------------
class Settings(BaseSettings):
    """
    Modelo de configuración de la aplicación.
    
    Esta clase define todas las variables de configuración necesarias
    para ejecutar la API. Los valores pueden venir de variables de
    entorno o del archivo .env.
    
    Attributes:
        api_key: Clave secreta para autenticar peticiones a la API
        api_host: Host donde escucha la API (default: todas las interfaces)
        api_port: Puerto de la API (default: 8000)
        ollama_host: Hostname del servidor Ollama (default: 'ollama' para Docker)
        ollama_port: Puerto del servidor Ollama (default: 11434)
        model_name: Nombre del modelo de IA a usar
        app_name: Nombre público de la aplicación
        app_version: Versión actual de la API
        debug: Modo debug activado/desactivado
    """
    
    # -------------------------------------------------------------------------
    # Configuración de la API
    # -------------------------------------------------------------------------
    api_key: str  # Requerido - debe estar en .env o variables de entorno
    api_host: str = "0.0.0.0"  # Escucha en todas las interfaces de red
    api_port: int = 8000  # Puerto estándar para APIs REST
    
    # -------------------------------------------------------------------------
    # Configuración de Ollama (servidor de modelos de IA)
    # -------------------------------------------------------------------------
    ollama_host: str = "ollama"  # Nombre del servicio Docker
    ollama_port: int = 11434  # Puerto estándar de Ollama
    model_name: str = "qwen2.5:3b-instruct-q4_K_M"  # Modelo Qwen cuantizado
    
    # -------------------------------------------------------------------------
    # Configuración de la aplicación
    # -------------------------------------------------------------------------
    app_name: str = "Qwen API"  # Nombre mostrado en documentación
    app_version: str = "1.0.0"  # Versión semántica
    debug: bool = False  # Activar para logs detallados en desarrollo
    
    @property
    def ollama_base_url(self) -> str:
        """
        Construye la URL completa del servidor Ollama.
        
        Returns:
            str: URL en formato http://host:puerto
        """
        return f"http://{self.ollama_host}:{self.ollama_port}"
    
    class Config:
        """Configuración interna de Pydantic Settings."""
        env_file = ".env"  # Archivo de donde cargar variables
        case_sensitive = False  # Variables no distinguen mayúsculas/minúsculas


# -----------------------------------------------------------------------------
# FUNCIÓN DE ACCESO A CONFIGURACIÓN (SINGLETON)
# -----------------------------------------------------------------------------
@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia única de configuración.
    
    Usa el decorador @lru_cache para garantizar que solo se crea
    una instancia de Settings durante toda la vida de la aplicación
    (patrón Singleton). Esto evita leer el archivo .env múltiples veces.
    
    Returns:
        Settings: Instancia única de la configuración
    """
    return Settings()