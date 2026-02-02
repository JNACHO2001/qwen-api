# Qwen API

API REST para clasificación de procesos legales con IA (Qwen 2.5)

## Descripción

Clasifica procesos judiciales del Consejo de Estado colombiano relacionados con **DOLMEN** o **alumbrado público** usando el modelo Qwen 2.5 ejecutado localmente con Ollama.

### Características

- 100% Local - Sin conexión a APIs externas
- Privacidad Total - Los datos no salen del servidor
- Dockerizado - Despliegue fácil
- Autenticación por API Key

## Requisitos

- Docker Desktop
- 8 GB RAM mínimo
- 10 GB espacio en disco

## Instalación

```bash
# 1. Clonar el proyecto
git clone <repositorio>
cd qwen-api

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y cambiar API_KEY

# 3. Iniciar servicios
docker-compose up -d --build
```

La primera ejecución descarga el modelo (~2GB).

## Verificar instalación

```bash
curl http://localhost:8000/health
```

## Uso

### Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/` | No | Info de la API |
| GET | `/health` | No | Estado del servicio |
| GET | `/docs` | No | Documentación Swagger |
| POST | `/api/v1/clasificar` | Sí | Clasificar proceso |

### Clasificar proceso

```bash
curl -X POST "http://localhost:8000/api/v1/clasificar" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_api_key" \
  -d '{
    "texto_pdf_completo": "El demandante reclama por cobros de alumbrado público...",
    "contenido_demanda": "Demanda contra DOLMEN por servicios de iluminación"
  }'
```

### Respuesta

```json
{
  "es_relevante": true,
  "confianza": 0.9,
  "razon": "El texto menciona DOLMEN y servicios de alumbrado público",
  "metodo_clasificacion": "IA"
}
```

### Criterios de clasificación

**RELEVANTE:**
- Menciona DOLMEN
- Alumbrado público / iluminación pública
- Contratos o cobros de alumbrado

**NO RELEVANTE:**
- Otros servicios (agua, gas, electricidad residencial)
- Sin relación con alumbrado público

## Configuración (.env)

```env
# Requerido
API_KEY=tu_clave_secreta

# Opcional
API_PORT=8000
MODEL_NAME=qwen2.5:1.5b
OLLAMA_KEEP_ALIVE=60m
OLLAMA_NUM_PARALLEL=1
OLLAMA_NUM_THREADS=8
```

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Reconstruir
docker-compose up -d --build

# Entrar a Ollama
docker exec -it qwen-ollama bash

# Ver modelos
docker exec qwen-ollama ollama list
```

## Estructura

```
qwen-api/
├── docker-compose.yml
├── .env
├── .env.example
└── api/
    ├── Dockerfile
    └── app/
        ├── main.py
        ├── config.py
        ├── models.py
        ├── dependencies.py
        └── routers/
            ├── health.py
            └── analisis.py
```

## Tecnologías

- Python 3.11
- FastAPI
- Ollama
- Qwen 2.5 (1.5B)
- Docker
