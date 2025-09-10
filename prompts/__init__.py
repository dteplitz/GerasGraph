"""
Módulo de prompts para todos los agentes del sistema GerasGraph.

Este módulo centraliza todos los prompts utilizados por los diferentes agentes,
manteniendo la consistencia en español y facilitando el mantenimiento.
"""

from .profesor_prompts import *
from .summarizer_prompts import *
from .validate_reason_prompts import *
from .evaluate_close_prompts import *
from .end_conversation_prompts import *
from .greeting_prompts import *

__all__ = [
    
    # Profesor agent prompts
    "PROFESOR_AGENT_CONFIG",
    "PROFESOR_WITH_SUMMARY_PROMPT",
    "PROFESOR_EXPLANATION_TYPES",
    
    # Summarizer agent prompts
    "SUMMARIZER_AGENT_CONFIG",
    "SUMMARY_EXTEND_PROMPT",
    "SUMMARY_CREATE_PROMPT",
    "SUMMARY_EXTEND_WITH_CONTEXT",
    
    # Validate reason agent prompts
    "REASON_DETECTION_PROMPT",
    # Evaluate close agent prompts
    "EVALUATE_CLOSE_PROMPT",
    # End conversation agent prompts
    "END_CONVERSATION_PROMPT",
    
    # Greeting prompts
    "GREETING_MESSAGE"
]
