from typing import Dict, Any
from custom_types import QuestionType
from graph_interface import GraphInterface
from config import Config

class ChatService:
    """Servicio para manejar la lógica de negocio del chat"""
    
    def __init__(self):
        """Inicializar el servicio con la interfaz del grafo"""
        self.graph_interface = GraphInterface()
    
    def process_chat_message(self, message: str, session_id: str, question: str | QuestionType) -> Dict[str, Any]:
        """Procesar un mensaje de chat y retornar la respuesta
        
        Args:
            message: El mensaje del usuario
            session_id: ID de la sesión
            question: Tipo de pregunta actual
            tipo_objetivo: Si la pregunta es de objetivo, especifica el tipo elegido previamente
        """
        try:
            # Normalizar question: si es enum, usar su valor string
            if isinstance(question, QuestionType):
                question_value = question.value
            else:
                question_value = question
            # Se espera que question ya sea una de las variantes de QuestionType (incluyendo OBJETIVO_*)
            # Procesar el mensaje a través del grafo
            result = self.graph_interface.process_message(message, session_id, user=None, question=question_value)
            
            # Obtener la respuesta
            if result["messages"]:
                last_message = result["messages"][-1]
                response_text = last_message.content
                
                # Obtener el tipo de agente directamente del estado (más eficiente)
                agent_type = result.get("last_agent", "unknown")
                
                return {
                    "response": response_text,
                    "agent_type": agent_type,
                    "session_id": session_id,
                    "success": True
                }
            
            return {
                "response": "No se pudo generar respuesta",
                "agent_type": "unknown",
                "session_id": session_id,
                "success": False
            }
            
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "agent_type": "error",
                "session_id": session_id,
                "success": False
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtener el estado de salud del servicio"""
        return {
            "status": "healthy",
            "config": {
                "model": Config.GROQ_MODEL,
                "temperature": Config.GROQ_TEMPERATURE,
                "db_path": Config.DB_PATH
            }
        }
