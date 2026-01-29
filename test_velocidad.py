import requests
import time

API_URL = "http://localhost:8000/api/v1/clasificar"
API_KEY = "jogo_bonito_2001"  # Del .env actual

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

data = {
    "reg": "TEST001",
    "radicacion": "11001-03-15-000-2023-00001-00",
    "texto_pdf_completo": "El demandante reclama por cobros de alumbrado público facturados por DOLMEN."
}

# Test 1: Primera request (cold start)
print("\n=== TEST 1: COLD START (Primera request) ===")
inicio = time.time()
response = requests.post(API_URL, json=data, headers=headers)
fin = time.time()
tiempo_cold = fin - inicio

print(f"Tiempo: {tiempo_cold:.2f}s")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    resultado = response.json()
    print(f"Relevante: {resultado['es_relevante']}")
    print(f"Confianza: {resultado['confianza']}")
    print(f"Razón: {resultado['razon']}")

# Test 2: Segunda request inmediata (warm - con keep_alive)
print("\n=== TEST 2: WARM START (Request con modelo en memoria) ===")
time.sleep(2)
inicio = time.time()
response = requests.post(API_URL, json=data, headers=headers)
fin = time.time()
tiempo_warm = fin - inicio

print(f"Tiempo: {tiempo_warm:.2f}s")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    resultado = response.json()
    print(f"Relevante: {resultado['es_relevante']}")
    print(f"Confianza: {resultado['confianza']}")

# Resumen de mejora
print("\n=== RESUMEN ===")
print(f"Cold start: {tiempo_cold:.2f}s")
print(f"Warm start: {tiempo_warm:.2f}s")
if tiempo_cold > tiempo_warm:
    mejora = ((tiempo_cold - tiempo_warm) / tiempo_cold) * 100
    print(f"Mejora con keep_alive: {mejora:.1f}% más rápido")
print(f"\nObjetivo esperado:")
print(f"  - Cold start: 3-5s")
print(f"  - Warm start: 0.5-2s")
