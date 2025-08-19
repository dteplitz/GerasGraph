"""
Agente Niño para el grafo LangGraph.

Este agente responde como un niño de 8 años, con emoción y curiosidad.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage
from .base_agent import BaseAgent

class NiñoAgent(BaseAgent):
    """Agente que responde como un niño de 8 años"""
    
    def __init__(self, model):
        """Inicializar el agente con el modelo LLM"""
        super().__init__(model, "niño")
    
    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar el estado y responder como un niño"""
        print("---Niño Node---")
        
        # Get summary if it exists
        summary = state.get("summary", "")
        
        # Create system message with summary context if available
        if summary:
            system_content = f"Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño.\n\nResumen de la conversación anterior: {summary}"
        else:
            system_content = "Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño."
        
        system_message = SystemMessage(content=system_content)
        
        # Preparar el prompt completo para logging
        prompt_messages = [system_message] + state["messages"]
        prompt_text = self._prepare_prompt_text(prompt_messages)
        
        # Log del prompt completo
        self._log_prompt(state, prompt_text)
        
        # Invocar el modelo
        response = self.model.invoke(prompt_messages)
        
        # Retornar el resultado
        return {
            "messages": [response],
            "updated_at": None  # Se maneja automáticamente en BaseAgent
        }
