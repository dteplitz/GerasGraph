"""
Agente Anciano para el grafo LangGraph.

Este agente responde como un anciano sabio de 80 años, con experiencia y sabiduría.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage
from .base_agent import BaseAgent

class AncianoAgent(BaseAgent):
    """Agente que responde como un anciano sabio de 80 años"""
    
    def __init__(self, model):
        """Inicializar el agente con el modelo LLM"""
        super().__init__(model, "anciano")
    
    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar el estado y responder como un anciano"""
        print("---Anciano Node---")
        
        # Get summary if it exists
        summary = state.get("summary", "")
        
        # Importar los prompts específicos del agente anciano
        from prompts import ANCIANO_BASE_PROMPT, ANCIANO_WITH_SUMMARY_PROMPT
        
        # Create system message with summary context if available
        if summary:
            system_content = ANCIANO_WITH_SUMMARY_PROMPT.format(summary=summary)
        else:
            system_content = ANCIANO_BASE_PROMPT
        
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
