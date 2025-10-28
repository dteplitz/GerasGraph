"""
Módulo de agentes para el grafo LangGraph.

Este módulo contiene todos los agentes especializados que se ejecutan
en los diferentes nodos del grafo de conversación.
"""

from .base_agent import BaseAgent
from .profesor_openai_agent import ProfesorOpenAIAgent as ProfesorOpenAIAgent
from .profesor_agent import ProfesorAgent as GroqProfesorAgent

# Alias por defecto: exponer ProfesorAgent apuntando a la versión OpenAI
ProfesorAgent = ProfesorOpenAIAgent

from .summarizer_agent import SummarizerAgent
from .validate_reason_agent import ValidateReasonAgent
from .validate_message_agent import ValidateMessageAgent
from .evaluate_close_agent import EvaluateCloseAgent
from .confirmation_agent import ConfirmationAgent
from .end_conversation_agent import EndConversationAgent
from .agent_config import *
from .agent_utils import *

__all__ = [
    "BaseAgent",
    "ProfesorAgent",
    "ProfesorOpenAIAgent",
    "GroqProfesorAgent",
    "SummarizerAgent",
    "ValidateReasonAgent",
    "ValidateMessageAgent",
    "EvaluateCloseAgent",
    "ConfirmationAgent",
    "EndConversationAgent",
    # Configuraciones
    "SUMMARIZER_AGENT_CONFIG",
    # Utilidades
    "build_system_prompt",
    "format_messages_for_logging",
    "extract_response_content",
    "validate_state_fields",
    "get_state_summary",
    "count_messages"
]
