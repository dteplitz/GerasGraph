import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from custom_types import QuestionType
from typing import List, Optional
from chat_service import ChatService
from config import Config
from middleware import create_middleware_stack

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar Groq API Key
def setup_groq():
    """Configurar la API key de Groq"""
    if not Config.GROQ_API_KEY:
        api_key = input("Ingresa tu GROQ_API_KEY: ")
        os.environ["GROQ_API_KEY"] = api_key
        Config.GROQ_API_KEY = api_key

# Configurar Groq si no está configurado
if not Config.GROQ_API_KEY:
    if os.environ.get("GROQ_API_KEY"):
        Config.GROQ_API_KEY = os.environ["GROQ_API_KEY"]
    else:
        raise ValueError("GROQ_API_KEY no está configurada")

# Crear la aplicación FastAPI
app = FastAPI(title="Agente LangGraph API", version="1.0.0")

# Aplicar el stack completo de middleware
app = create_middleware_stack(app)

# Log seguro de configuración en startup (sin exponer secretos)
@app.on_event("startup")
def _log_startup_config():
    try:
        Config.print_config()
    except Exception as e:
        print(f"No se pudo imprimir la configuración: {e}")

# Inicializar el servicio de chat
chat_service = ChatService()

# Modelos de datos para la API
class ChatRequest(BaseModel):
    message: str
    session_id: str
    question: QuestionType | str

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    session_id: str

# Endpoints de la API
@app.get("/")
def read_root():
    return {"message": "Agente LangGraph API funcionando"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint para chatear con el agente"""
    try:
        # Procesar el mensaje a través del servicio
        result = chat_service.process_chat_message(
            message=request.message,
            session_id=request.session_id,
            question=request.question
        )
        
        if result["success"]:
            return ChatResponse(
                response=result["response"],
                agent_type=result["agent_type"],
                session_id=result["session_id"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["response"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health_check():
    """Endpoint de salud de la API"""
    return chat_service.get_health_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
