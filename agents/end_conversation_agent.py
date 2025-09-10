"""
Agente EndConversation para el grafo LangGraph.

Este agente finaliza la conversación cuando el usuario ha confirmado
su elección y está listo para terminar.
"""

from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .base_agent import BaseAgent
from prompts.end_conversation_prompts import END_CONVERSATION_PROMPT

class EndConversationAgent(BaseAgent):
    """Agente que finaliza la conversación"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(EndConversationAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente end conversation solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el end conversation
            from langchain_groq import ChatGroq
            from config import Config

            # Crear modelo específico del end conversation con parámetros optimizados
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.7,  # Temperatura media para mensajes más naturales
                max_tokens=400    # Respuestas más largas para despedida
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "end_conversation")

            # Marcar como inicializado
            self._initialized = True

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        print("---End Conversation Node---")
        
        # Obtener el estado actual
        current_status = state.get("status", "")
        
        # Solo procesar si el estado es "confirmed"
        if current_status != "confirmed":
            print(f"[EndConversation] Estado actual '{current_status}' no es 'confirmed', retornando sin cambios")
            return state
        
        # Obtener información del estado
        current_question = state.get("question", "")
        reason = state.get("reason", "")
        
        # Si no hay pregunta o razón, crear mensaje genérico
        if not current_question or not reason:
            print(f"[EndConversation] Faltan pregunta o razón, creando mensaje genérico")
            end_message = "Perfecto, has completado tu consulta. ¡Que tengas un excelente día!"
        else:
            # Crear el prompt para generar mensaje de despedida personalizado
            end_prompt = END_CONVERSATION_PROMPT.format(
                current_question=current_question,
                reason=reason
            )

            # Preparar mensajes para el modelo
            system_message = SystemMessage(content=end_prompt)
            human_message = HumanMessage(content="Genera un mensaje de despedida personalizado")
            messages_for_analysis = [system_message, human_message]
            
            # Usar el modelo para generar el mensaje
            response = self.model.invoke(messages_for_analysis)
            end_message = response.content

        # Crear mensaje de despedida
        farewell_message = AIMessage(content=end_message)
        
        # Actualizar el estado
        state["status"] = "end_conversation"
        state["completion_message"] = end_message
        state["last_agent"] = "end_conversation"
        
        # Agregar el mensaje de despedida
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(farewell_message)
        
        print(f"[EndConversation] Conversación finalizada con mensaje: {end_message[:100]}...")
        
        # Retornar el estado modificado
        return state
