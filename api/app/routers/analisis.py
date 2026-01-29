"""
=============================================================================
ROUTER DE CLASIFICACIÓN - analisis.py
=============================================================================
Endpoint para clasificar procesos legales del Consejo de Estado colombiano.

Funcionalidad:
- Clasificación de procesos relacionados con DOLMEN o alumbrado público

Requiere autenticación mediante API Key.
=============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException  # Herramientas de FastAPI
import ollama  # Cliente para el servidor de modelos Ollama
import json  # Para parsear respuestas JSON
from app.config import get_settings  # Configuración de la aplicación
from app.models import ProcesoLegalRequest, ProcesoLegalResponse  # Modelos de datos
from app.dependencies import verificar_api_key  # Dependencia de autenticación

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ROUTER
# -----------------------------------------------------------------------------
router = APIRouter()  # Router para agrupar endpoints de análisis
settings = get_settings()  # Configuración global de la aplicación

# -----------------------------------------------------------------------------
# PROMPT DEL CLASIFICADOR
# -----------------------------------------------------------------------------
# Define el prompt para clasificar procesos legales
# El placeholder {texto} será reemplazado con el texto del proceso
PROMPTS = {
    "clasificar_dolmen": """
     TAREA:
     Clasificar un proceso judicial colombiano como RELEVANTE o NO RELEVANTE
     respecto a ALUMBRADO PÚBLICO o la empresa DOLMEN.

REGLA PRIORITARIA (OBLIGATORIA):
Si el texto contiene literalmente AL MENOS UNA de las siguientes expresiones:
- "alumbrado"
- "alumbrado público"
- "iluminación pública"

ENTONCES la clasificación DEBE ser:
"es_relevante": true
y la confianza DEBE ser >= 0.7

REGLAS DE RELEVANCIA:
También es RELEVANTE si menciona:
- "DOLMEN"
- contratos de alumbrado público
- servicio de alumbrado público
- cobros, tarifas, facturación o prestación del alumbrado público

REGLAS DE NO RELEVANCIA:
Es NO RELEVANTE si el texto trata EXCLUSIVAMENTE de:
- agua, gas, energía residencial, alcantarillado
- otros contratos que NO sean de alumbrado público
- demandas sin relación con alumbrado
- uso figurativo de la palabra "luz" (ej: "a la luz de la ley")

IMPORTANTE:
- El tipo de proceso (tutela, ordinario, etc.) NO afecta la decisión
- El demandado (municipio, empresa, persona) NO afecta la decisión
- No inventar información
- No interpretar fuera de las reglas

CONFIDENCIA:
- 0.9 → menciona "DOLMEN" + alumbrado público
- 0.7 → mención clara de alumbrado o iluminación pública
- 0.5 → relación probable pero ambigua
- 0.3 → mención débil o indirecta
- 0.0 → no relacionado

RESTRICCIONES:
- NO explicar
- NO agregar texto fuera del JSON
- RESPONDER SOLO JSON válido

FORMATO DE RESPUESTA EXACTO:
{{"es_relevante": true/false, "confianza": 0.0, "razon": "máx 100 caracteres"}}

TEXTO A CLASIFICAR:
{texto}
"""
}


# -----------------------------------------------------------------------------
# ENDPOINT DE CLASIFICACIÓN DE PROCESOS LEGALES
# -----------------------------------------------------------------------------
@router.post("/clasificar", response_model=ProcesoLegalResponse, tags=["Clasificación"])
async def clasificar_proceso(
    request: ProcesoLegalRequest,
    api_key: str = Depends(verificar_api_key)
):
    """
    Clasifica procesos legales relacionados con DOLMEN o alumbrado público.

    Recibe un proceso judicial completo y devuelve el mismo objeto con
    los campos de clasificación agregados (es_relevante, confianza, razon).

    Args:
        request: Objeto completo del proceso judicial
        api_key: API key validada (inyectada por Depends)

    Returns:
        ProcesoLegalResponse: Proceso completo con clasificación agregada

    Raises:
        HTTPException: Error 500 si falla el procesamiento
    """
    try:
        client = ollama.Client(host=settings.ollama_base_url)

        # Usar texto_pdf_completo o contenido_demanda para clasificar
        texto_clasificar = request.texto_pdf_completo or request.contenido_demanda

        if not texto_clasificar:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar texto_pdf_completo o contenido_demanda"
            )

        prompt = PROMPTS["clasificar_dolmen"].format(texto=texto_clasificar)

      
        
        response = client.chat(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.0,      # 🔒 Determinístico
                "top_p": 0.1,            # 🔒 Reduce creatividad
                "num_predict": 80,       # ⚡ Suficiente para JSON
                "repeat_penalty": 1.1    # 🧹 Evita repeticiones
        },
                                            # 🧠 Corta justo al final del JSON
          keep_alive="15m"
        )

        resultado = json.loads(response['message']['content'])

        # Devolver el objeto completo con clasificación
        return ProcesoLegalResponse(
            reg=request.reg,
            radicacion=request.radicacion,
            ponente=request.ponente,
            demandante=request.demandante,
            demandado=request.demandado,
            clase=request.clase,
            fecha_providencia=request.fecha_providencia,
            actuacion=request.actuacion,
            documento=request.documento,
            fecha_estado=request.fecha_estado,
            pdf_descargado=request.pdf_descargado,
            ruta_pdf=request.ruta_pdf,
            texto_pdf_completo=request.texto_pdf_completo,
            contenido_demanda=request.contenido_demanda,
            es_relevante=resultado["es_relevante"],
            confianza=resultado["confianza"],
            razon=resultado["razon"][:150],
            keywords_encontrados=[],
            metodo_clasificacion="IA"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al parsear respuesta JSON del modelo: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))