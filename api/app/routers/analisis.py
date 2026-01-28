"""
=============================================================================
ROUTER DE ANÁLISIS - analisis.py
=============================================================================
Contiene los endpoints principales para análisis de texto con IA.

Funcionalidades:
- Análisis individual de textos
- Procesamiento batch de múltiples textos
- Diferentes tipos de tareas (resumir, sentimiento, extraer, etc.)

Todos los endpoints requieren autenticación mediante API Key.
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException  # Herramientas de FastAPI
import ollama  # Cliente para el servidor de modelos Ollama
from app.config import get_settings  # Configuración de la aplicación
from app.models import AnalisisRequest, AnalisisResponse  # Modelos de datos
from app.dependencies import verificar_api_key  # Dependencia de autenticación

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ROUTER
# -----------------------------------------------------------------------------
router = APIRouter()  # Router para agrupar endpoints de análisis
settings = get_settings()  # Configuración global de la aplicación

# -----------------------------------------------------------------------------
# DICCIONARIO DE PROMPTS
# -----------------------------------------------------------------------------
# Define los prompts del sistema para cada tipo de tarea
# El placeholder {texto} será reemplazado con el texto del usuario
PROMPTS = {
    "analizar": "Analiza en detalle el siguiente texto:\n\n{texto}",
    "resumir": "Resume de manera concisa el siguiente texto:\n\n{texto}",
    "sentimiento": "Analiza el sentimiento (positivo, negativo, neutral) y explica:\n\n{texto}",
    "extraer": "Extrae las ideas principales y conceptos clave:\n\n{texto}",
    "keywords": "Extrae las palabras clave más importantes:\n\n{texto}"
}


# -----------------------------------------------------------------------------
# ENDPOINT DE ANÁLISIS INDIVIDUAL
# -----------------------------------------------------------------------------
@router.post("/analizar", response_model=AnalisisResponse, tags=["Análisis"])
async def analizar_texto(
    request: AnalisisRequest,  # Datos de entrada validados por Pydantic
    api_key: str = Depends(verificar_api_key)  # Requiere autenticación
):
    """
    Analiza texto según la tarea especificada.
    
    Este endpoint envía el texto al modelo Qwen a través de Ollama
    y retorna el resultado del análisis.
    
    **Tareas disponibles:**
    - `analizar`: Análisis detallado del texto
    - `resumir`: Resumen conciso
    - `sentimiento`: Análisis de sentimiento
    - `extraer`: Extracción de ideas principales
    - `keywords`: Palabras clave
    
    Args:
        request: Objeto con texto, tarea y parámetros del modelo
        api_key: API key validada (inyectada por Depends)
        
    Returns:
        AnalisisResponse: Resultado del análisis con metadatos
        
    Raises:
        HTTPException: Error 500 si falla el procesamiento
    """
    try:
        # Creamos el cliente de Ollama con la URL del servidor
        client = ollama.Client(host=settings.ollama_base_url)
        
        # Construimos el prompt reemplazando {texto} con el texto del usuario
        prompt = PROMPTS[request.tarea].format(texto=request.texto)
        
        # Enviamos la petición al modelo de IA
        response = client.chat(
            model=settings.model_name,  # Modelo configurado (ej: qwen2.5:3b)
            messages=[{'role': 'user', 'content': prompt}],  # Mensaje del usuario
            options={
                'temperature': request.temperatura,  # Creatividad (0.0 - 2.0)
                'num_predict': request.max_tokens  # Límite de tokens de salida
            }
        )
        
        # Construimos y retornamos la respuesta estandarizada
        return AnalisisResponse(
            status="success",
            tarea=request.tarea,
            resultado=response['message']['content'],  # Texto generado por el modelo
            modelo=settings.model_name,
            tokens_usados=response.get('eval_count')  # Tokens consumidos (opcional)
        )
        
    except Exception as e:
        # Capturamos cualquier error y lo reportamos como 500
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el análisis: {str(e)}"
        )


# -----------------------------------------------------------------------------
# ENDPOINT DE ANÁLISIS BATCH (MÚLTIPLES TEXTOS)
# -----------------------------------------------------------------------------
@router.post("/batch", tags=["Análisis"])
async def batch_analizar(
    textos: list[str],  # Lista de textos a procesar
    tarea: str = "analizar",  # Tipo de análisis (mismo para todos)
    api_key: str = Depends(verificar_api_key)  # Requiere autenticación
):
    """
    Analiza múltiples textos en batch.
    
    Procesa una lista de textos secuencialmente, aplicando la misma
    tarea de análisis a todos. Útil para procesar grandes volúmenes
    de datos.
    
    **Nota de rendimiento**: Los textos se procesan uno por uno.
    Para mejor rendimiento en producción, considerar implementar
    procesamiento paralelo con asyncio o un sistema de colas.
    
    Args:
        textos: Lista de textos a analizar
        tarea: Tipo de tarea (aplica a todos los textos)
        api_key: API key validada
        
    Returns:
        dict: Resumen con total, exitosos, fallidos y resultados detallados
    """
    resultados = []  # Lista para almacenar resultados de cada texto
    
    # Iteramos sobre cada texto con su índice
    for idx, texto in enumerate(textos):
        try:
            # Creamos un request individual para cada texto
            req = AnalisisRequest(texto=texto, tarea=tarea)
            
            # Reutilizamos el endpoint de análisis individual
            resultado = await analizar_texto(req, api_key)
            
            # Agregamos el resultado exitoso
            resultados.append({
                "index": idx,  # Posición original del texto
                "status": "success",
                "resultado": resultado.resultado
            })
            
        except Exception as e:
            # Si falla un texto, lo marcamos como error pero continuamos
            resultados.append({
                "index": idx,
                "status": "error",
                "error": str(e)  # Mensaje del error
            })
    
    # Retornamos un resumen con estadísticas y todos los resultados
    return {
        "total": len(textos),  # Cantidad total de textos recibidos
        "exitosos": sum(1 for r in resultados if r["status"] == "success"),
        "fallidos": sum(1 for r in resultados if r["status"] == "error"),
        "resultados": resultados  # Detalle de cada análisis
    }