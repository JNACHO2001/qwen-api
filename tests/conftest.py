"""
=============================================================================
CONFIGURACIÓN DE PYTEST - conftest.py
=============================================================================
Este archivo configura pytest para que pueda encontrar los módulos de la app.

¿Qué es conftest.py?
- Es un archivo especial de pytest
- Se ejecuta automáticamente antes de los tests
- Aquí configuramos el path de Python para importar 'app'

Sin este archivo, pytest no podría encontrar 'from app.config import ...'
=============================================================================
"""
import sys
from pathlib import Path

# Agregamos la carpeta 'api' al path de Python
# Esto permite que 'from app.xxx import yyy' funcione en los tests
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))
