"""
Configuración centralizada para todos los agentes del grafo LangGraph.

Este módulo ahora importa los prompts desde los módulos específicos de cada agente.
"""

from prompts import (
    PROFESOR_AGENT_CONFIG,
    SUMMARIZER_AGENT_CONFIG
)

# Re-exportar las configuraciones para mantener compatibilidad
__all__ = [
    "PROFESOR_AGENT_CONFIG",
    "SUMMARIZER_AGENT_CONFIG"
]
