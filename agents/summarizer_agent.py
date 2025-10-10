"""
Agente de Resumen para el grafo LangGraph.

Este agente se encarga de crear y extender resúmenes de las conversaciones.
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, RemoveMessage
from .base_agent import BaseAgent

class SummarizerAgent(BaseAgent):
    """Agente que resume las conversaciones"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(SummarizerAgent, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el agente summarizer solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el summarizer
            from langchain_groq import ChatGroq
            from config import Config
            
            # Crear modelo específico del summarizer
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.3,  # Baja temperatura para resúmenes más precisos
                max_tokens=800    # Tokens suficientes para resúmenes detallados
            )
            
            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "summarizer")
            
            # Marcar como inicializado
            self._initialized = True
    
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
        
        # Extraer el texto de la respuesta de forma segura
        from .agent_utils import extract_text_from_content
        summary_text = extract_text_from_content(getattr(response, "content", response))
        
        # Eliminar todos los mensajes excepto los 2 más recientes
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        
        # Retornar el resultado
        return {
            "summary": summary_text,
            "messages": delete_messages,
            "last_agent": "summarizer"  # Consistente con otros agentes
        }
