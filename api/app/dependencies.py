"""
=============================================================================
MÓDULO DE DEPENDENCIAS - dependencies.py
=============================================================================
Define las dependencias inyectables para los endpoints de FastAPI.

Las dependencias son funciones que se ejecutan antes del endpoint y pueden:
- Validar autenticación/autorización
- Obtener conexiones a bases de datos
- Realizar verificaciones previas

Se inyectan usando el parámetro Depends() en los endpoints.
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from fastapi import Header, HTTPException, status  # Herramientas de FastAPI
from app.config import get_settings  # Configuración de la aplicación

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
# -----------------------------------------------------------------------------
# Obtenemos la configuración para acceder a la API key esperada
settings = get_settings()


# -----------------------------------------------------------------------------
# DEPENDENCIA DE AUTENTICACIÓN
# -----------------------------------------------------------------------------
async def verificar_api_key(
    x_api_key: str = Header(
        ...,  # Campo requerido
        description="API Key para autenticación"  # Descripción en Swagger
    )
):
    """
    Valida la API key enviada en el header de la petición.
    
    Esta función se usa como dependencia en endpoints protegidos.
    Compara el valor del header 'X-API-Key' con la clave configurada.
    
    Args:
        x_api_key: Valor del header X-API-Key (inyectado automáticamente)
        
    Returns:
        str: La API key si es válida
        
    Raises:
        HTTPException: Error 401 si la API key es inválida o no está presente
        
    Uso:
        @router.post("/endpoint")
        async def mi_endpoint(api_key: str = Depends(verificar_api_key)):
            # El endpoint solo se ejecuta si la API key es válida
            pass
    """
    # Comparamos la key recibida con la configurada
    if x_api_key != settings.api_key:
        # Si no coincide, rechazamos la petición con error 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Código HTTP 401
            detail="API Key inválida",  # Mensaje de error
            headers={"WWW-Authenticate": "ApiKey"}  # Header de autenticación
        )
    
    # Si es válida, retornamos la key (disponible en el endpoint si se necesita)
    return x_api_key