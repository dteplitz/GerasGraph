"""
Configuración centralizada para todos los agentes del grafo LangGraph.

Este módulo ahora importa los prompts desde los módulos específicos de cada agente.
"""

from prompts import (
    NIÑO_AGENT_CONFIG,
    ANCIANO_AGENT_CONFIG,
    PROFESOR_AGENT_CONFIG,
    SUMMARIZER_AGENT_CONFIG,
    ROUTER_AGENT_CONFIG,
    GRAPH_CONFIG
)

# Re-exportar las configuraciones para mantener compatibilidad
__all__ = [
    "NIÑO_AGENT_CONFIG",
    "ANCIANO_AGENT_CONFIG",
    "PROFESOR_AGENT_CONFIG",
    "SUMMARIZER_AGENT_CONFIG",
    "ROUTER_AGENT_CONFIG",
    "GRAPH_CONFIG"
]
