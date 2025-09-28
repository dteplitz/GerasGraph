"""
Agente Profesor para el grafo LangGraph.

Este agente responde como un profesor experto en finanzas personales,
con un enfoque educativo, profesional y didáctico.
"""

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from .base_agent import BaseAgent

class ProfesorAgent(BaseAgent):
    """Agente que responde como un profesor experto en finanzas personales"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(ProfesorAgent, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el agente profesor solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el profesor
            from langchain_groq import ChatGroq
            from config import Config
            
            # Crear modelo específico del profesor con parámetros optimizados
            self.model = ChatGroq(
                api_key=Config.GROQ_API_KEY,
                model=Config.GROQ_MODEL,
                temperature=0.2,  # Más preciso para explicaciones
                max_tokens=800    # Respuestas detalladas
            )
            
            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "profesor")
            
            # Marcar como inicializado
            self._initialized = True
    
    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar el estado y responder como un profesor"""
        print("---Profesor Node---")
        
        # Importar la configuración del agente profesor
        from prompts import PROFESOR_AGENT_CONFIG, PROFESOR_WITH_SUMMARY_PROMPT
        from prompts.profesor_prompts import PROFESOR_BASE_BY_TYPE
        from prompts.greeting_prompts import GREETING_BY_TYPE
        
        # Get summary if it exists
        summary = state.get("summary", "")
        # Resolver cuestión legible (si la pregunta es enum key)
        current_question = state.get("question", "")
        readable_question = GREETING_BY_TYPE.get(current_question, current_question)
        
        # Seleccionar base por tipo de pregunta (fallback a base genérica)
        base_template = PROFESOR_BASE_BY_TYPE.get(current_question, PROFESOR_AGENT_CONFIG['base_prompt'])
        # Rellenar plantilla con la pregunta legible si aplica
        try:
            base_filled = base_template.format(question=readable_question)
        except Exception:
            base_filled = base_template

        # Create system message with summary context if available
        if summary:
            system_content = PROFESOR_WITH_SUMMARY_PROMPT.format(
                base_prompt=base_filled,
                summary=summary
            )
        else:
            system_content = base_filled
        
        system_message = SystemMessage(content=system_content)
        
        # Prepare messages for the model
        messages = [system_message] + state["messages"]
        
        # Preparar el prompt completo para logging
        prompt_text = self._prepare_prompt_text(messages)
        
        # Log del prompt completo
        self._log_prompt(state, prompt_text)
        
        # Usar el modelo propio del agente (ya configurado en __init__)
        response = self.model.invoke(messages)
        
        # Retornar el resultado
        return {
            "messages": [response]
            # updated_at se maneja automáticamente en BaseAgent
        }
