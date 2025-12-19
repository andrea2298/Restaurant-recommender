Restaurant Recommender 🍽️

Este proyecto integra FastAPI, n8n y OpenAI para recomendar restaurantes cercanos a una ciudad y país indicados.  
El flujo recibe datos desde un frontend, consulta a OpenAI y devuelve un JSON con las recomendaciones de restaurantes.

------------------------------------------------------------
Comenzando:
Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

------------------------------------------------------------
Pre-requisitos:
- Python 3.10+
- FastAPI y Uvicorn
  _pip install fastapi uvicorn_
- n8n (Docker o npm)
  npm install n8n -g
- Cuenta de OpenAI y una API Key válida

------------------------------------------------------------
Instalación:
1. Clonar el repositorio
   git clone https://github.com/andrea2298/Restaurant-recommender.git
   cd Restaurant-recommender

2. Configurar entorno Python
   python3 -m venv venv
   source venv/bin/activate   # En Linux/Mac
   venv\Scripts\activate      # En Windows
   pip install -r requirements.txt

3. Levantar FastAPI
   uvicorn main:app --reload --port 8000

4. Configurar n8n
   - Importa el workflow Restaurant Recommender.json
   - Activa el workflow en http://localhost:5678
   - Verifica que el Webhook esté disponible en:
     http://localhost:5678/webhook/openai-restaurants

5. Probar con PowerShell
   Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/openai-restaurants -Body @{city="mexicali"; country="mexico"} | ConvertTo-Json -Depth 5

Ejemplo de respuesta esperada:
{
  "restaurants": [
    {
      "name": "La Casa de la Abuela",
      "cuisine": "Mexicana",
      "location": "Centro de Mexicali",
      "price_range": "$$",
      "rating": 4.5,
      "highlight": "Pozole rojo"
    },
    {
      "name": "Mariscos El Güero",
      "cuisine": "Mariscos",
      "location": "Zona Río",
      "price_range": "$",
      "rating": 4.2,
      "highlight": "Ceviche de camarón"
    },
    {
      "name": "Il Forno",
      "cuisine": "Italiana",
      "location": "Plaza La Cachanilla",
      "price_range": "$$$",
      "rating": 4.7,
      "highlight": "Pizza al horno de leña"
    }
  ]
}

------------------------------------------------------------
Ejecutando las pruebas:
Pruebas end-to-end:
Verifican que el flujo completo (FastAPI → Webhook → OpenAI → Respond to Webhook) devuelva un JSON válido con restaurantes.
Ejemplo:
pytest tests/test_end_to_end.py

Pruebas de estilo de codificación:
Se usa flake8 para validar que el código cumple con PEP8.
flake8 app/

------------------------------------------------------------
Despliegue:
- En producción se recomienda usar Docker Compose para levantar FastAPI y n8n juntos.
- Configura variables de entorno para la API Key de OpenAI.
- Usa un proxy inverso (NGINX) para exponer los endpoints de manera segura.

------------------------------------------------------------
Construido con:
- FastAPI - Framework web para el backend
- n8n - Orquestador de flujos automatizados
- OpenAI API - Motor de generación de texto
- Docker - Contenedores para despliegue
- PowerShell / curl - Pruebas de integración

------------------------------------------------------------
Autores:
- Andrea Almanza – Trabajo inicial, integración y documentación
------------------------------------------------------------

