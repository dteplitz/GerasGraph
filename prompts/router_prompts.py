"""
Prompts para el agente Router del sistema GerasGraph.

Este módulo contiene todos los prompts específicos para el agente Router,
que se encarga de decidir el flujo de la conversación y cuándo resumir.
"""

# Configuración del Router
ROUTER_AGENT_CONFIG = {
    "available_agents": ["niño", "anciano", "profesor"],
    "summary_threshold": 6,  # Número de mensajes antes de resumir
    "default_route": "niño"
}

# Configuración general del grafo
GRAPH_CONFIG = {
    "max_messages_before_summary": 6,
    "summary_keep_messages": 2,
    "default_status": "greeting"
}

# Mensajes de debug para el router
ROUTER_DEBUG_MESSAGES = {
    "greet_selected": "Router seleccionó: greet (primera vez)",
    "agent_selected": "Router seleccionó: {agent}",
    "evaluating_continue": "Evaluando continuar: {count} mensajes",
    "activating_summary": "¡Activando summary! Más de 6 mensajes",
    "continuing_normal": "Continuando conversación normal"
}
