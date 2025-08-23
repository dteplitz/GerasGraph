"""
Agente de Resumen para el grafo LangGraph.

Este agente se encarga de crear y extender resúmenes de las conversaciones.
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, RemoveMessage
from .base_agent import BaseAgent

class SummarizerAgent(BaseAgent):
    """Agente que resume las conversaciones"""
    
    def __init__(self, model):
        """Inicializar el agente con el modelo LLM"""
        super().__init__(model, "summarize_conversation")
    
    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar el estado y crear/extender el resumen"""
        print("---Resumen de Conversación---")
        
        # Obtener el resumen existente si existe
        summary = state.get("summary", "")
        
        # Importar los prompts específicos del agente summarizer
        from prompts import SUMMARY_EXTEND_PROMPT, SUMMARY_CREATE_PROMPT, SUMMARY_EXTEND_WITH_CONTEXT
        
        # Crear el prompt de resumen
        if summary:
            summary_message = SUMMARY_EXTEND_WITH_CONTEXT.format(
                summary=summary,
                extend_prompt=SUMMARY_EXTEND_PROMPT
            )
        else:
            summary_message = SUMMARY_CREATE_PROMPT
        
        # Agregar el prompt a nuestro historial
        messages = state["messages"] + [HumanMessage(content=summary_message)]
        
        # Preparar el prompt completo para logging
        prompt_text = self._prepare_prompt_text(messages)
        
        # Log del prompt completo
        self._log_prompt(state, prompt_text)
        
        # Invocar el modelo
        response = self.model.invoke(messages)
        
        # Eliminar todos los mensajes excepto los 2 más recientes y agregar el resumen al estado
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        
        # Retornar el resultado
        return {
            "summary": response.content, 
            "messages": delete_messages,
            "updated_at": None  # Se maneja automáticamente en BaseAgent
        }
