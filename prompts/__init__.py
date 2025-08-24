"""
Módulo de prompts para todos los agentes del sistema GerasGraph.

Este módulo centraliza todos los prompts utilizados por los diferentes agentes,
manteniendo la consistencia en español y facilitando el mantenimiento.
"""

from .niño_prompts import *
from .anciano_prompts import *
from .profesor_prompts import *
from .summarizer_prompts import *
from .router_prompts import *
from .greeting_prompts import *

__all__ = [
    # Niño agent prompts
    "NIÑO_AGENT_CONFIG",
    "NIÑO_WITH_SUMMARY_PROMPT",
    
    # Anciano agent prompts
    "ANCIANO_AGENT_CONFIG",
    "ANCIANO_WITH_SUMMARY_PROMPT",
    
    # Profesor agent prompts
    "PROFESOR_AGENT_CONFIG",
    "PROFESOR_WITH_SUMMARY_PROMPT",
    "PROFESOR_EXPLANATION_TYPES",
    
    # Summarizer agent prompts
    "SUMMARIZER_AGENT_CONFIG",
    "SUMMARY_EXTEND_PROMPT",
    "SUMMARY_CREATE_PROMPT",
    "SUMMARY_EXTEND_WITH_CONTEXT",
    
    # Router agent prompts
    "REASON_DETECTION_PROMPT",
    
    # Greeting prompts
    "GREETING_MESSAGE"
]
