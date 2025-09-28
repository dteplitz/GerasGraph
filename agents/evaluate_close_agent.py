"""
Agente EvaluateClose para el grafo LangGraph.

Este agente evalúa si la conversación está lista para cerrar
y decide el siguiente paso basado en el estado actual del usuario.
"""

from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from .base_agent import BaseAgent
from prompts.evaluate_close_prompts import EVALUATE_CLOSE_PROMPT

class EvaluateCloseAgent(BaseAgent):
    """Agente que evalúa si la conversación está lista para cerrar"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(EvaluateCloseAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente evaluate close solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el evaluate close
            from langchain_groq import ChatGroq
            from config import Config

            # Crear modelo específico del evaluate close con parámetros optimizados
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.1,  # Baja temperatura para decisiones consistentes
                max_tokens=300    # Respuestas concisas para decisiones
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "evaluate_close")

            # Marcar como inicializado
            self._initialized = True

    def _parse_decision_response(self, response_content: str) -> str:
        """Parsear la respuesta del modelo para extraer la decisión"""
        try:
            import json
            
            # Limpiar la respuesta de posibles caracteres extra
            cleaned_response = response_content.strip()
            
            # Intentar parsear como JSON
            try:
                parsed = json.loads(cleaned_response)
                decision = parsed.get("decision", "")
                return decision
                    
            except json.JSONDecodeError:
                # Fallback: buscar patrones si el JSON no es válido
                if "confirmation" in response_content.lower():
                    return "confirmation"
                elif "end_conversation" in response_content.lower():
                    return "end_conversation"
                elif "profesor" in response_content.lower():
                    return "profesor"
                else:
                    return "profesor"  # default
                    
        except Exception as e:
            print(f"Error parseando decisión: {e}")
            return "profesor"  # default seguro

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        print("---Evaluate Close Node---")
        
        # Obtener el estado actual
        current_status = state.get("status", "")
        
        # Solo procesar si el estado es "waiting_confirmation"
        if current_status != "waiting_confirmation":
            print(f"[EvaluateClose] Estado actual '{current_status}' no es 'waiting_confirmation', retornando sin cambios")
            return state
        
        # Obtener información del estado
        current_question = state.get("question", "")
        reason = state.get("reason", "")
        
        # Si no hay pregunta o razón, ir al profesor
        if not current_question or not reason:
            print(f"[EvaluateClose] Faltan pregunta o razón, yendo al profesor")
            state["status"] = "exploring"
            return state

        # Crear el prompt para decidir el siguiente paso
        decision_prompt = EVALUATE_CLOSE_PROMPT.format(
            current_question=current_question,
            reason=reason
        )

        # Preparar mensajes para el modelo
        system_message = SystemMessage(content=decision_prompt)
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

        messages_for_analysis = [system_message, user_message]
        
        # Usar el modelo para decidir
        response = self.model.invoke(messages_for_analysis)
        
        # Parsear la decisión
        decision = self._parse_decision_response(response.content)

        # Log del resultado
        print(f"[EvaluateClose] Decisión tomada: {decision}")
        
        # Aplicar la decisión al estado
        if decision == "confirmation":
            state["status"] = "asking_confirmation"
        elif decision == "end_conversation":
            state["status"] = "confirmed"
        elif decision == "profesor":
            state["status"] = "exploring"
        else:
            # Default: ir al profesor
            state["status"] = "exploring"
        
        print(f"[EvaluateClose] Estado actualizado a: {state['status']}")
        
        # Retornar el estado modificado
        return state
