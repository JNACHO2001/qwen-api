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
    "clasificar_dolmen": """Eres un asistente especializado en clasificar procesos legales del Consejo de Estado colombiano.

Tu tarea es determinar si un proceso judicial está relacionado con la empresa DOLMEN o con servicios de alumbrado público.

CRITERIOS PARA CLASIFICAR COMO RELEVANTE:
1. El proceso menciona explícitamente a DOLMEN (empresa de alumbrado público)
2. Se trata de servicios de alumbrado público, iluminación pública o luminarias
3. Se mencionan contratos, obligaciones o reclamaciones sobre alumbrado público
4. Involucra postes de luz, servicios de iluminación urbana/residencial
5. Reclamos por cobros o facturación de alumbrado público

CRITERIOS PARA CLASIFICAR COMO NO RELEVANTE:
1. Procesos sobre otros servicios públicos (agua, gas, alcantarillado, energía eléctrica residencial)
2. Demandas sobre otros temas administrativos sin relación con alumbrado
3. Procesos laborales, penales o civiles sin mención de alumbrado público
4. Casos donde "luz" o "iluminación" se mencionen en contextos diferentes (ej: "a la luz de los hechos")

NIVEL DE CONFIANZA:
- 0.9-1.0: Mención explícita de DOLMEN o múltiples términos de alumbrado público
- 0.7-0.89: Clara relación con alumbrado público sin mencionar DOLMEN
- 0.5-0.69: Relación probable pero con ambigüedad
- 0.3-0.49: Relación dudosa o muy indirecta
- 0.0-0.29: No hay relación aparente

IMPORTANTE:
- Analiza TODO el texto, no solo las primeras líneas
- Presta especial atención a los antecedentes y pretensiones
- Si hay duda razonable, es mejor clasificar como NO relevante (confianza < 0.6)

Responde SOLO con JSON:
{{
  "es_relevante": true,
  "confianza": 0.95,
  "razon": "máximo 150 caracteres"
}}

{texto}"""
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
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.2, 'num_predict': 300}
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