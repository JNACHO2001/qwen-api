# Qwen API

API REST para clasificación de procesos legales con IA (Qwen 2.5)

## Descripción

Clasifica procesos judiciales del Consejo de Estado colombiano relacionados con **DOLMEN** o **alumbrado público** usando el modelo Qwen 2.5 ejecutado localmente con Ollama.

### Características

- 100% Local - Sin conexión a APIs externas
- Privacidad Total - Los datos no salen del servidor
- Dockerizado - Despliegue fácil
- Autenticación por API Key
- CI automatizado con GitHub Actions

---

## Requisitos Previos

| Requisito | Versión Mínima | Verificar con |
|-----------|----------------|---------------|
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Git | 2.0+ | `git --version` |
| RAM | 8 GB mínimo | `free -h` |
| Disco | 10 GB libres | `df -h` |

---

## Guía de Instalación Paso a Paso (Linux)

### Paso 1: Instalar Docker

```bash
# Actualizar paquetes del sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias necesarias
sudo apt install -y ca-certificates curl gnupg

# Agregar la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar el repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine y Docker Compose
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar tu usuario al grupo docker (para no usar sudo cada vez)
sudo usermod -aG docker $USER

# IMPORTANTE: Cerrar sesión y volver a entrar para que el cambio de grupo tome efecto
# O ejecutar temporalmente:
newgrp docker

# Verificar que Docker funciona
docker --version
docker compose version
```

### Paso 2: Clonar el Repositorio

```bash
# Navegar a la carpeta donde quieres guardar el proyecto
cd ~/Documents

# Clonar el repositorio
git clone https://github.com/tu-usuario/qwen-api.git

# Entrar a la carpeta del proyecto
cd qwen-api
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo con nano (o tu editor favorito)
nano .env
```

Configurar los valores dentro del archivo `.env`:

```env
# OBLIGATORIO - Cambiar por una clave segura
API_KEY=tu_clave_secreta_aqui

# OPCIONAL - Puerto de la API (por defecto 8000)
API_PORT=8000

# OPCIONAL - Modelo a usar
MODEL_NAME=qwen2.5:3b
```

Guardar y salir de nano: `Ctrl + O` → `Enter` → `Ctrl + X`

### Paso 4: Configurar la Carpeta de Modelos

```bash
# Crear la carpeta donde se guardarán los modelos de Ollama
mkdir -p ~/.ollama

# Verificar que se creó
ls -la ~/.ollama
```

Editar el archivo `docker-compose.yml` para apuntar al volumen correcto:

```bash
nano docker-compose.yml
```

Buscar la sección de volúmenes del servicio `ollama` y cambiar la ruta:

```yaml
volumes:
  # Cambiar por tu ruta de usuario
  - /home/tu-usuario/.ollama:/root/.ollama
```

### Paso 5: Construir e Iniciar los Contenedores

```bash
# Construir las imágenes e iniciar los servicios en segundo plano
docker compose up -d --build

# Verificar que los contenedores estén corriendo
docker ps
```

Deberías ver dos contenedores activos:

```
CONTAINER ID   IMAGE          STATUS                   NAMES
abc123...      ollama/ollama  Up 2 minutes (healthy)   qwen-ollama
def456...      qwen-api       Up 2 minutes             qwen-api
```

### Paso 6: Descargar el Modelo dentro del Contenedor

Este es el paso más importante. El modelo de IA se descarga **dentro** del contenedor de Ollama.

```bash
# 1. Verificar que el contenedor de Ollama está corriendo
docker ps | grep qwen-ollama

# 2. Entrar al contenedor de Ollama
docker exec -it qwen-ollama bash

# 3. Dentro del contenedor: descargar el modelo principal
ollama pull qwen2.5:3b

# 4. Verificar que el modelo se descargó correctamente
ollama list

# 5. (Opcional) Probar el modelo directamente
ollama run qwen2.5:3b "Hola, ¿funciona correctamente?"

# 6. Salir del contenedor
exit
```

**Tamaño aproximado de los modelos:**

| Modelo | Tamaño | RAM requerida |
|--------|--------|---------------|
| qwen2.5:0.5b | ~400 MB | 4 GB |
| qwen2.5:1.5b | ~1.5 GB | 6 GB |
| qwen2.5:3b | ~2.5 GB | 8 GB |

### Paso 7: Persistir el Modelo en el Host

Los modelos se persisten automáticamente gracias al volumen configurado en el Paso 4. Esto significa que si detienes o eliminas el contenedor, los modelos **no se pierden**.

```bash
# Verificar que los modelos están en tu máquina host
ls -la ~/.ollama/models/

# Deberías ver esta estructura:
# .ollama/
# ├── models/
# │   ├── blobs/          # Archivos binarios de los modelos
# │   └── manifests/      # Metadatos de los modelos

# Ver el tamaño total de los modelos descargados
du -sh ~/.ollama/models/
```

Para comprobar que la persistencia funciona:

```bash
# Detener y eliminar los contenedores
docker compose down

# Volver a iniciar (los modelos siguen ahí)
docker compose up -d

# Verificar que el modelo sigue disponible
docker exec qwen-ollama ollama list
```

### Paso 8: Copiar Modelos a Otro Servidor

Si necesitas mover los modelos a otro equipo Linux sin volver a descargarlos:

**En el servidor origen (exportar):**

```bash
# Crear un backup comprimido de los modelos
tar -czf ollama-models-backup.tar.gz -C ~/.ollama .

# Ver el tamaño del backup
ls -lh ollama-models-backup.tar.gz

# Copiar al servidor destino usando scp
scp ollama-models-backup.tar.gz usuario@servidor-destino:/tmp/
```

**En el servidor destino (importar):**

```bash
# Crear la carpeta de destino
mkdir -p ~/.ollama

# Extraer los modelos
tar -xzf /tmp/ollama-models-backup.tar.gz -C ~/.ollama

# Verificar que se extrajeron correctamente
ls -la ~/.ollama/models/

# Iniciar los contenedores (los modelos ya están disponibles)
docker compose up -d

# Verificar que Ollama detecta los modelos
docker exec qwen-ollama ollama list
```

### Paso 9: Verificar la Instalación Completa

```bash
# Verificar que la API responde
curl http://localhost:8000/health

# Respuesta esperada:
# {"status": "healthy", "modelo": "qwen2.5:3b", ...}

# Ver la documentación Swagger en el navegador:
# http://localhost:8000/docs
```

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
MODEL_NAME=qwen2.5:3b
OLLAMA_KEEP_ALIVE=60m
OLLAMA_NUM_PARALLEL=1
OLLAMA_NUM_THREADS=8
```

---

## CI - Integración Continua

El proyecto usa **GitHub Actions** para ejecutar los tests automáticamente cada vez que se hace push o se abre un Pull Request en la rama `develop-DOLMEN`.

### ¿Cómo funciona?

```
Push a develop-DOLMEN
        │
        ▼
GitHub crea un servidor Ubuntu temporal
        │
        ▼
Clona el repositorio
        │
        ▼
Instala Python 3.12 y dependencias
        │
        ▼
Ejecuta pytest (15 tests)
        │
        ▼
   ✅ PASS  o  ❌ FAIL
```

### Archivo de configuración

El workflow está en [.github/workflows/ci.yml](.github/workflows/ci.yml) y se ejecuta automáticamente. No necesitas hacer nada extra.

### Ver los resultados

1. Ir al repositorio en GitHub
2. Click en la pestaña **Actions**
3. Verás el historial de ejecuciones con su estado (verde = pasó, rojo = falló)

---

## Comandos Útiles

### Gestión de Contenedores

```bash
# Ver estado de los contenedores
docker ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs solo de la API
docker compose logs -f api

# Ver logs solo de Ollama
docker compose logs -f ollama

# Reiniciar todos los servicios
docker compose restart

# Detener todos los servicios
docker compose down

# Reconstruir e iniciar
docker compose up -d --build
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
docker exec -it qwen-ollama ollama run qwen2.5:3b "Hola, ¿cómo estás?"
```

### Solución de Problemas

```bash
# Ver uso de recursos (CPU, RAM por contenedor)
docker stats

# Reiniciar solo Ollama
docker compose restart ollama

# Ver logs de errores
docker compose logs --tail=50 api

# Verificar conectividad interna entre contenedores
docker exec qwen-api curl http://ollama:11434/api/tags
```

---

## Estructura del Proyecto

```
qwen-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de CI (GitHub Actions)
├── docker-compose.yml
├── .env                        # Variables de entorno (no subir a git)
├── .env.example                # Ejemplo de configuración
├── .gitignore                  # Archivos ignorados por git
├── requirements.txt            # Dependencias Python
├── tests/                      # Tests automatizados
│   ├── conftest.py             # Configuración de pytest
│   ├── test_config.py          # Tests de configuración
│   ├── test_models.py          # Tests de modelos Pydantic
│   └── test_api.py             # Tests de endpoints
└── api/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── config.py
        ├── models.py
        ├── dependencies.py
        └── routers/
            ├── health.py
            └── analisis.py
```

---

## Tests

El proyecto incluye tests automatizados para verificar el correcto funcionamiento de la API.

### Estructura de Tests

| Archivo | Descripción | Tests |
|---------|-------------|-------|
| `test_config.py` | Verifica la configuración de la aplicación | 4 |
| `test_models.py` | Verifica los modelos Pydantic | 5 |
| `test_api.py` | Verifica los endpoints de la API | 6 |

### Ejecutar Tests (dentro de Docker)

```bash
# Copiar los tests al contenedor (solo la primera vez)
docker cp tests qwen-api:/app/tests

# Ejecutar todos los tests
docker exec qwen-api python -m pytest tests/ -v
```

### Comandos de Pytest

```bash
# Ejecutar todos los tests con detalle
docker exec qwen-api python -m pytest tests/ -v

# Ejecutar solo tests de modelos
docker exec qwen-api python -m pytest tests/test_models.py -v

# Ejecutar solo tests de API
docker exec qwen-api python -m pytest tests/test_api.py -v

# Ejecutar solo tests de configuración
docker exec qwen-api python -m pytest tests/test_config.py -v

# Ejecutar tests sin traceback largo
docker exec qwen-api python -m pytest tests/ -v --tb=short
```

### Resultado Esperado

```
tests/test_api.py::test_endpoint_raiz PASSED
tests/test_api.py::test_endpoint_docs PASSED
tests/test_api.py::test_clasificar_sin_api_key PASSED
tests/test_api.py::test_clasificar_api_key_incorrecta PASSED
tests/test_api.py::test_clasificar_sin_texto PASSED
tests/test_api.py::test_estructura_respuesta_raiz PASSED
tests/test_config.py::test_api_key_existe PASSED
tests/test_config.py::test_valores_por_defecto PASSED
tests/test_config.py::test_ollama_base_url PASSED
tests/test_config.py::test_singleton_settings PASSED
tests/test_models.py::test_health_response_valido PASSED
tests/test_models.py::test_proceso_legal_request_minimo PASSED
tests/test_models.py::test_proceso_legal_request_completo PASSED
tests/test_models.py::test_proceso_legal_response PASSED
tests/test_models.py::test_pydantic_validacion_tipos PASSED

======================== 15 passed ========================
```

---

## Solución de Problemas Comunes

### El contenedor de Ollama no inicia

```bash
# Verificar memoria disponible (mínimo 8 GB)
free -h

# Ver logs de error
docker compose logs ollama
```

### Error "model not found"

```bash
# El modelo no está descargado. Descargarlo con:
docker exec qwen-ollama ollama pull qwen2.5:3b
```

### La API no responde

```bash
# Verificar que ambos contenedores estén corriendo
docker ps

# Verificar que Ollama esté saludable
docker exec qwen-ollama ollama list

# Reiniciar los servicios
docker compose restart
```

### Los modelos no persisten después de reiniciar

Verificar que el volumen esté correctamente configurado en `docker-compose.yml`:

```yaml
volumes:
  - /home/tu-usuario/.ollama:/root/.ollama
```

---

## Tecnologías

- Python 3.12
- FastAPI
- Pydantic
- Ollama
- Qwen 2.5 (3B)
- Docker / Docker Compose
- Pytest (testing)
- GitHub Actions (CI)

---

## Licencia

MIT
