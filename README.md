# Qwen API

API REST para clasificación de procesos legales con IA (Qwen 2.5)

## Descripción

Clasifica procesos judiciales del Consejo de Estado colombiano relacionados con **DOLMEN** o **alumbrado público** usando el modelo Qwen 2.5 ejecutado localmente con Ollama.

### Características

- 100% Local - Sin conexión a APIs externas
- Privacidad Total - Los datos no salen del servidor
- Dockerizado - Despliegue fácil
- Autenticación por API Key

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

| Requisito | Versión Mínima | Verificar con |
|-----------|----------------|---------------|
| Docker Desktop | 4.0+ | `docker --version` |
| Git | 2.0+ | `git --version` |
| RAM | 8 GB mínimo | - |
| Disco | 10 GB libres | - |

---

## Guía de Instalación Paso a Paso

### Paso 1: Clonar el Repositorio desde GitHub

```bash
# Abrir terminal (CMD o PowerShell en Windows)

# Navegar a la carpeta donde quieres guardar el proyecto
cd C:\Users\TuUsuario\Documents

# Clonar el repositorio
git clone https://github.com/tu-usuario/qwen-api.git

# Entrar a la carpeta del proyecto
cd qwen-api
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# En Linux/Mac usar:
# cp .env.example .env
```

Editar el archivo `.env` con un editor de texto y configurar:

```env
# OBLIGATORIO - Cambiar por una clave segura
API_KEY=tu_clave_secreta_aqui

# OPCIONAL - Puerto de la API (por defecto 8000)
API_PORT=8000

# OPCIONAL - Modelo a usar
MODEL_NAME=qwen2.5:1.5b
```

### Paso 3: Configurar la Carpeta de Modelos

Antes de iniciar, debes configurar dónde se guardarán los modelos de Ollama en tu equipo.

**En Windows:**
```bash
# Crear carpeta para modelos (si no existe)
mkdir C:\Users\TuUsuario\.ollama
```

**En Linux/Mac:**
```bash
mkdir -p ~/.ollama
```

Luego, editar el archivo `docker-compose.yml` y cambiar la línea del volumen:

```yaml
volumes:
  # Cambiar esta ruta por tu carpeta de usuario
  - C:\Users\TuUsuario\.ollama:/root/.ollama   # Windows
  # - ~/.ollama:/root/.ollama                   # Linux/Mac
```

### Paso 4: Iniciar los Contenedores

```bash
# Construir e iniciar los servicios
docker-compose up -d --build

# Verificar que los contenedores estén corriendo
docker ps
```

Deberías ver dos contenedores:
- `qwen-ollama` - Servidor de modelos
- `qwen-api` - API REST

### Paso 5: Descargar los Modelos en Ollama

Una vez que los contenedores estén corriendo, debes descargar el modelo dentro del contenedor de Ollama:

```bash
# Entrar al contenedor de Ollama
docker exec -it qwen-ollama bash

# Dentro del contenedor, descargar el modelo principal
ollama pull qwen2.5:1.5b

# (Opcional) Descargar otros modelos
ollama pull qwen2.5:3b      # Modelo más grande (mejor calidad)
ollama pull qwen2.5:0.5b    # Modelo más pequeño (más rápido)

# Ver los modelos descargados
ollama list

# Salir del contenedor
exit
```

**Tamaño aproximado de los modelos:**
| Modelo | Tamaño | RAM requerida |
|--------|--------|---------------|
| qwen2.5:0.5b | ~400 MB | 4 GB |
| qwen2.5:1.5b | ~1.5 GB | 6 GB |
| qwen2.5:3b | ~2.5 GB | 8 GB |

### Paso 6: Verificar que los Modelos están en tu Equipo

Los modelos se guardan automáticamente en la carpeta que configuraste en el Paso 3.

**Verificar en Windows:**
```bash
# Ver contenido de la carpeta de modelos
dir C:\Users\TuUsuario\.ollama\models
```

**Verificar en Linux/Mac:**
```bash
ls -la ~/.ollama/models
```

La estructura de carpetas será:
```
.ollama/
├── models/
│   ├── blobs/          # Archivos binarios de los modelos
│   └── manifests/      # Metadatos de los modelos
└── ...
```

### Paso 7: Verificar la Instalación Completa

```bash
# Verificar que la API responde
curl http://localhost:8000/health

# O abrir en el navegador:
# http://localhost:8000/health
# http://localhost:8000/docs  (Documentación Swagger)
```

Respuesta esperada:
```json
{"status": "healthy", "model": "qwen2.5:1.5b"}
```

---

## Copiar Modelos a Otro Equipo

Si necesitas mover los modelos a otro equipo sin volver a descargarlos:

### Exportar (desde el equipo origen)

```bash
# Copiar la carpeta completa de modelos
# Windows:
xcopy /E /I C:\Users\TuUsuario\.ollama C:\backup\ollama-models

# Linux/Mac:
cp -r ~/.ollama ~/backup/ollama-models
```

### Importar (en el equipo destino)

```bash
# Copiar los modelos a la ubicación correcta
# Windows:
xcopy /E /I C:\backup\ollama-models C:\Users\TuUsuario\.ollama

# Linux/Mac:
cp -r ~/backup/ollama-models ~/.ollama
```

Luego, en el equipo destino, solo necesitas iniciar los contenedores y los modelos estarán disponibles.

---

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

## Comandos Útiles

### Gestión de Contenedores

```bash
# Ver estado de los contenedores
docker ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo de la API
docker-compose logs -f api

# Ver logs solo de Ollama
docker-compose logs -f ollama

# Reiniciar todos los servicios
docker-compose restart

# Detener todos los servicios
docker-compose down

# Reconstruir e iniciar
docker-compose up -d --build
```

### Gestión de Modelos en Ollama

```bash
# Entrar al contenedor de Ollama
docker exec -it qwen-ollama bash

# Ver modelos instalados
docker exec qwen-ollama ollama list

# Descargar un nuevo modelo
docker exec qwen-ollama ollama pull qwen2.5:3b

# Eliminar un modelo
docker exec qwen-ollama ollama rm qwen2.5:0.5b

# Probar un modelo directamente
docker exec -it qwen-ollama ollama run qwen2.5:1.5b "Hola, ¿cómo estás?"
```

### Solución de Problemas

```bash
# Ver uso de recursos
docker stats

# Reiniciar solo Ollama
docker-compose restart ollama

# Ver logs de errores
docker-compose logs --tail=50 api

# Verificar conectividad interna
docker exec qwen-api curl http://ollama:11434/api/tags
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

## Solución de Problemas Comunes

### El contenedor de Ollama no inicia

```bash
# Verificar que Docker tiene suficiente memoria asignada
# En Docker Desktop: Settings > Resources > Memory (mínimo 8 GB)

# Ver logs de error
docker-compose logs ollama
```

### Error "model not found"

```bash
# El modelo no está descargado. Descargarlo con:
docker exec qwen-ollama ollama pull qwen2.5:1.5b
```

### La API no responde

```bash
# Verificar que ambos contenedores estén corriendo
docker ps

# Verificar que Ollama esté saludable
docker exec qwen-ollama ollama list

# Reiniciar los servicios
docker-compose restart
```

### Los modelos no persisten después de reiniciar

Verificar que el volumen esté correctamente configurado en `docker-compose.yml`:
```yaml
volumes:
  - C:\Users\TuUsuario\.ollama:/root/.ollama
```

---

## Tecnologías

- Python 3.11
- FastAPI
- Ollama
- Qwen 2.5 (1.5B)
- Docker

---

## Licencia

MIT
