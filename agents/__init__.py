"""
Módulo de agentes para el grafo LangGraph.

Este módulo contiene todos los agentes especializados que se ejecutan
en los diferentes nodos del grafo de conversación.
"""

from .base_agent import BaseAgent
from .niño_agent import NiñoAgent
from .anciano_agent import AncianoAgent
from .profesor_agent import ProfesorAgent
from .summarizer_agent import SummarizerAgent
from .router_agent import RouterAgent
from .confirmation_agent import ConfirmationAgent
from .agent_config import *
from .agent_utils import *

__all__ = [
    "BaseAgent",
    "NiñoAgent", 
    "AncianoAgent",
    "ProfesorAgent",
    "SummarizerAgent",
    "RouterAgent",
    "ConfirmationAgent",
    # Configuraciones
    "NIÑO_AGENT_CONFIG",
    "ANCIANO_AGENT_CONFIG", 
    "SUMMARIZER_AGENT_CONFIG",
    # Utilidades
    "build_system_prompt",
    "format_messages_for_logging",
    "extract_response_content",
    "validate_state_fields",
    "get_state_summary",
    "count_messages"
]
