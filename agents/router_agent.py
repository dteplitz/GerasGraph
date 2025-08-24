"""
Agente Router mejorado para el grafo LangGraph.

Este agente analiza si el usuario ha proporcionado una razón explícita
en respuesta a una pregunta y determina el flujo de la conversación.
"""

from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from .base_agent import BaseAgent
from prompts.router_prompts import REASON_DETECTION_PROMPT

class RouterAgent(BaseAgent):
    """Agente que detecta razones explícitas y rutea la conversación"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(RouterAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente router solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el router
            from langchain_groq import ChatGroq
            from config import Config

            # Crear modelo específico del router con parámetros optimizados
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.1,  # Baja temperatura para análisis consistente
                max_tokens=300    # Respuestas concisas para análisis
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "router")

            # Marcar como inicializado
            self._initialized = True

    def _parse_simple_response(self, response_content: str) -> tuple[bool, str]:
        """Parsear la respuesta JSON del modelo"""
        try:
            import json

            # Limpiar la respuesta y buscar JSON
            response_clean = response_content.strip()

            # Intentar parsear como JSON
            try:
                json_data = json.loads(response_clean)
                has_response = json_data.get("has_response", 0)
                reason = json_data.get("reason", None)
                return has_response == 1, reason
            except json.JSONDecodeError:
                # Si no es JSON válido, loguear y continuar
                print(f"[Router] Formato de respuesta incorrecto: '{response_content}'")
                return False, None

        except Exception as e:
            print(f"[Router] Error parseando respuesta: {str(e)}")
            return False, None

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        # Obtener información del estado
        current_question = state.get("question", "")

        # Si no hay pregunta en el estado, pasar directo al profesor
        if not current_question:
            print(f"[Router] No hay pregunta en el estado, pasando directo al profesor")
            return state

        # Obtener el último mensaje del usuario
        messages = state.get("messages", [])
        if not messages:
            return state

        # Obtener el último mensaje del usuario
        user_message = ""
        if messages:
            # En LangGraph, el último mensaje es el más reciente
            last_message = messages[-1]
            user_message = last_message.content

        if not user_message:
            return state

        # Crear el prompt para detectar respuestas
        detection_prompt = REASON_DETECTION_PROMPT.format(
            current_question=current_question,
            user_message=user_message
        )

        # Preparar mensajes para el modelo
        system_message = SystemMessage(content=detection_prompt)
        human_message = HumanMessage(content=user_message)
        messages_for_analysis = [system_message, human_message]
        

        # Usar el modelo para analizar
        response = self.model.invoke(messages_for_analysis)
        
        # Parsear la respuesta (debe ser 1 o 0)
        has_response, reason = self._parse_simple_response(response.content)
        
        # Log del resultado
        print(f"[Router] Usuario {'respondió' if has_response else 'NO respondió'} a la pregunta")
        if reason:
            # Guardar la razon en el estado
            state["reason"] = reason
            # Actualiza status de la conversacion a waiting_confirmation
            state["status"] = "waiting_confirmation"
            print(f"[Router] Razón: {reason}")
        
        # Retornar el estado (puede ser modificado si es necesario)
        return state
