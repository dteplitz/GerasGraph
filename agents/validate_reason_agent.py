"""
Agente ValidateReason para el grafo LangGraph.

Este agente valida si el usuario ha proporcionado una razón válida
en respuesta a una pregunta y determina el flujo inicial de la conversación.
"""

from typing import Dict, Any, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from .base_agent import BaseAgent
from prompts.validate_reason_prompts import REASON_DETECTION_PROMPT

class ValidateReasonAgent(BaseAgent):
    """Agente que valida si el usuario dio una razón válida"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(ValidateReasonAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente validate reason solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el validate reason
            from langchain_groq import ChatGroq
            from config import Config

            # Crear modelo específico del validate reason con parámetros optimizados
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.1,  # Baja temperatura para análisis consistente
                max_tokens=300    # Respuestas concisas para análisis
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "validate_reason")

            # Marcar como inicializado
            self._initialized = True

    def _parse_simple_response(self, response_content: str) -> tuple[bool, str]:
        """Parsear la respuesta del modelo para extraer has_response y reason"""
        try:
            import json
            
            # Limpiar la respuesta de posibles caracteres extra
            cleaned_response = response_content.strip()
            
            # Intentar parsear como JSON
            try:
                parsed = json.loads(cleaned_response)
                has_response = parsed.get("has_response", 0)
                reason = parsed.get("reason")
                
                if has_response == 1 and reason:
                    return True, reason
                else:
                    return False, None
                    
            except json.JSONDecodeError:
                # Fallback: buscar patrones si el JSON no es válido
                if '"has_response": 1' in response_content:
                    # Extraer la razón usando regex o búsqueda de strings
                    if '"reason":' in response_content:
                        reason_start = response_content.find('"reason":') + 9
                        reason_end = response_content.find('"', reason_start)
                        if reason_end > reason_start:
                            reason = response_content[reason_start:reason_end].strip()
                            return True, reason
                    return True, "opción válida"
                else:
                    return False, None
                    
        except Exception as e:
            print(f"Error parseando respuesta: {e}")
            return False, None

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        print("---Validate Reason Node---")
        
        # Obtener el estado actual
        current_status = state.get("status", "")
        
        # Solo procesar si el estado es "exploring"
        if current_status != "exploring":
            print(f"[ValidateReason] Estado actual '{current_status}' no es 'exploring', retornando sin cambios")
            return state
        
        # Obtener información del estado
        current_question = state.get("question", "")

        # Si no hay pregunta en el estado, mantener estado exploring
        if not current_question:
            print(f"[ValidateReason] No hay pregunta en el estado, manteniendo estado exploring")
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
        print(f"[ValidateReason] Usuario {'respondió' if has_response else 'NO respondió'} a la pregunta")
        if reason:
            # Guardar la razon en el estado
            state["reason"] = reason
            # Actualiza status de la conversacion a asking_confirmation
            state["status"] = "asking_confirmation"
            print(f"[ValidateReason] Razón: {reason}")
        else:
            # Si no hay razón válida, mantener estado exploring
            state["status"] = "exploring"
            print(f"[ValidateReason] No se detectó razón válida, continuando explorando")
        
        # Retornar el estado (puede ser modificado si es necesario)
        return state
