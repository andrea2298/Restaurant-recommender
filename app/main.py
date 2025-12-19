from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from PIL import Image
from typing import Optional
from sqlalchemy import text

import httpx
import os
import logging
import io
import base64

from db import SessionLocal, engine
from models import Restaurant
from seed import init_db

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.on_event("startup")
def startup_event():
    logging.info("Inicializando base de datos...")
    init_db()
    logging.info("Base de datos lista para usar.")

templates = Jinja2Templates(directory="templates")

N8N_WEBHOOK_URL = os.getenv("N8N_URL", "http://localhost:5678/webhook/openai-cities")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommendations", response_class=HTMLResponse)
async def recommendations(
    request: Request,
    city: str = Form(...),
    country: str = Form(...)
):
    try:
        payload = {"city": city, "country": country}
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                N8N_WEBHOOK_URL,
                json=payload,
                timeout=30
            )

        if response.status_code != 200:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Error al consultar n8n."}
            )
        
        data = response.json()
        cities = data.get("cities", [])

        if not cities:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "No se encontraron ciudades."}
            )
        
        results = {}
        with SessionLocal() as session:
            for c in cities:
                query = (
                    session.query(Restaurant)
                    .filter(Restaurant.city.ilike(f"%{c}%"))
                    .order_by(
                        Restaurant.avg_rating.desc(),
                        Restaurant.price.asc(),
                        Restaurant.total_ratings.desc()
                    )
                    .limit(3)
                    .all()
                )
                results[c] = query

        return templates.TemplateResponse(
            "recommendations.html",
            {"request": request, "results": results}
        )
    
    except httpx.ConnectError:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "No se pudo conectar con n8n."}
        )

    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Tiempo de espera agotado."}
        )
    
    except Exception as e:
        logging.error(f"Error interno en recommendations: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Error interno: {str(e)}"}
        )

def validate_image_file(file_bytes: bytes) -> tuple[bool, str]:
    """Validación de archivos de imagen"""
    MAX_SIZE = 10 * 1024 * 1024 
    if len(file_bytes) > MAX_SIZE:
        return False, f"La imagen es demasiado grande. Máximo {MAX_SIZE/1024/1024}MB."
    
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        img = Image.open(io.BytesIO(file_bytes))
        width, height = img.size

        if width > 10000 or height > 10000:
            return False, "Dimensiones de imagen demasiado grandes."
        if width < 10 or height < 10:
            return False, "Dimensiones de imagen demasiado pequeñas."
        
        return True, "Imagen válida"
    except Exception as e:
        return False, f"Imagen corrupta o inválida: {str(e)}"

@app.post("/api/chat")
async def chat_assistant(
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    if not message and not image:
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un mensaje de texto o una imagen."
        )
    
    try:
        system_message = {
            "role": "system",
            "content": (
                "Eres un asistente gastronómico especializado. "
                "Tu objetivo es recomendar platillos típicos de ciudades y países. "
                "Sé preciso, útil y conciso. "
                "Si el usuario sube una imagen, describe lo que ves y su relación con gastronomía local."
            )
        }
        
        messages = [system_message]
        
        if image:
            image_bytes = await image.read()
            await image.seek(0)
            
            is_valid, validation_msg = validate_image_file(image_bytes)
            if not is_valid:
                raise HTTPException(status_code=400, detail=validation_msg)
            
            user_content = []
            if message:
                user_content.append({"type": "text", "text": message})
            else:
                user_content.append({"type": "text", "text": "Describe esta imagen en relación a gastronomía local."})
            
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = image.content_type or "image/jpeg"
            
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
            })
            
            messages.append({"role": "user", "content": user_content})
            model = "gpt-4-vision-preview"
            
        elif message:
            messages.append({"role": "user", "content": message})
            model = "gpt-3.5-turbo"
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        return {
            "response": response.choices[0].message.content,
            "model_used": model,
            "tokens_used": response.usage.total_tokens if response.usage else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en chat_assistant: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del chatbot: {str(e)}"
        )

@app.get("/health") 
def health_check(): 
    """Endpoint de salud para monitoreo""" 
    
    try: 
        with SessionLocal() as session: 
            session.execute(text("SELECT 1")) 
            
            return { 
                "status": "healthy", 
                "database": "connected", 
                "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured" 
            } 
        
    except Exception as e: 
        return JSONResponse( 
            status_code=503, 
            content={"status": "unhealthy", "error": str(e)} 
        )
