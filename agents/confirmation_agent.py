"""
Agente Confirmador para el grafo LangGraph.

Este agente se ejecuta cuando el usuario ha proporcionado una razón válida
y necesita confirmar su elección antes de continuar.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from .base_agent import BaseAgent
from prompts.confirmation_prompts import CONFIRMATION_PROMPT

class ConfirmationAgent(BaseAgent):
    """Agente que pide confirmación de la razón del usuario"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(ConfirmationAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente confirmador solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el confirmador
            from langchain_groq import ChatGroq
            from config import Config

            # Crear modelo específico del confirmador
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.7,  # Temperatura media para respuestas más naturales
                max_tokens=500    # Respuestas más largas para confirmaciones
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "confirmation")

            # Marcar como inicializado
            self._initialized = True

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        print("---Confirmation Node---")
        
        # Obtener la razón del usuario del estado
        reason = state.get("reason", "")
        
        # Obtener el tipo de pregunta actual y resolverlo a texto legible
        current_question = state.get("question", "")
        
        # Importar el mapping para resolver la pregunta
        from prompts.greeting_prompts import GREETING_BY_TYPE
        
        # Resolver pregunta actual a texto legible
        question_text = ""
        if current_question:
            mapping = GREETING_BY_TYPE.get(current_question)
            if isinstance(mapping, dict):
                # Si el mapping tiene "question", usar ese campo
                question_text = mapping.get("question", current_question)
            elif isinstance(mapping, str):
                question_text = mapping
            else:
                question_text = current_question
        
        if not question_text:
            question_text = "tu plan de retiro"
        
        print(f"[Confirmation] Pregunta: {question_text}")
        print(f"[Confirmation] Razón: {reason}")
        
        # Crear el prompt de confirmación con contexto
        confirmation_prompt = CONFIRMATION_PROMPT.format(
            question=question_text,
            reason=reason
        )
        
        # Preparar mensajes para el modelo
        system_message = SystemMessage(content=confirmation_prompt)
        human_message = HumanMessage(content="Por favor confirma mi elección")
        messages_for_analysis = [system_message, human_message]
        
        # Usar el modelo para generar la confirmación
        response = self.model.invoke(messages_for_analysis)
        
        # Crear mensaje de confirmación
        from langchain_core.messages import AIMessage
        confirmation_message = AIMessage(content=response.content)
        
        # Retornar solo los campos que se actualizan
        return {
            "messages": [confirmation_message],
            "status": "waiting_confirmation",  # Cambiar estado a waiting_confirmation
            "last_agent": "confirmation"  # Marcar que el agente confirmador respondió
            # updated_at se maneja automáticamente en BaseAgent
        }
