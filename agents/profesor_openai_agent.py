"""
Agente Profesor (versión OpenAI) para el grafo LangGraph.

Este agente responde como un profesor experto en finanzas personales,
utilizando el modelo de ChatGPT (OpenAI) en lugar de Groq.
"""

from typing import Dict, Any
import os
from langchain_core.messages import SystemMessage
from .base_agent import BaseAgent


class ProfesorOpenAIAgent(BaseAgent):
    """Agente que responde como un profesor usando ChatGPT (OpenAI)"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(ProfesorOpenAIAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente profesor (OpenAI) solo una vez"""
        if not self._initialized:
            # Configurar el modelo específico para el profesor con OpenAI
            from langchain_openai import ChatOpenAI
            try:
                from config import Config
            except Exception:
                Config = None  # Fallback si no existe

            # Leer configuración desde Config si existe, si no desde variables de entorno
            api_key = (
                getattr(Config, "OPENAI_API_KEY", None) if Config else None
            ) or os.getenv("OPENAI_API_KEY", "")
            model_name = (
                getattr(Config, "OPENAI_MODEL", None) if Config else None
            ) or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            # Crear modelo específico del profesor con parámetros optimizados
            self.model = ChatOpenAI(
                 api_key=api_key,
                 model=model_name,
                 temperature=0.2,  # Más preciso para explicaciones
                 max_tokens=800,   # Respuestas detalladas
                 output_version="responses/v1",
                 use_responses_api=True,
            )

            # Cargar vector store id desde configuración o entorno
            vector_store_id = (
                getattr(Config, "OPENAI_VECTOR_STORE_ID", None) if Config else None
            ) or os.getenv("OPENAI_VECTOR_STORE_ID", "")

            # Guardar como lista para herramientas (si está disponible)
            self.vector_store_ids = [vector_store_id] if vector_store_id else []

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "profesor_openai")

            # Marcar como inicializado
            self._initialized = True

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar el estado y responder como un profesor (OpenAI)"""
        print("---Profesor (OpenAI) Node---")

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
        base_template = PROFESOR_BASE_BY_TYPE.get(
            current_question, PROFESOR_AGENT_CONFIG['base_prompt']
        )
        # Rellenar plantilla con la pregunta legible si aplica
        try:
            base_filled = base_template.format(question=readable_question)
        except Exception:
            base_filled = base_template

        # Create system message with summary context if available
        if summary:
            system_content = PROFESOR_WITH_SUMMARY_PROMPT.format(
                base_prompt=base_filled,
                summary=summary,
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
        response = self.model.invoke(
            messages,
            tools=[{
                "type": "file_search",
                "vector_store_ids": ["vs_68d9c8f01e0c8191b2d3642556f08071"]
            }],
        )

        # Extraer el texto de la respuesta de forma segura
        from .agent_utils import extract_text_from_content
        response_text = extract_text_from_content(getattr(response, "content", response))

        # Crear mensaje de respuesta limpio
        from langchain_core.messages import AIMessage
        response_message = AIMessage(content=response_text)

        # Retornar el resultado
        return {
            "messages": [response_message],
            "last_agent": "profesor"  # Consistente con otros agentes
        }