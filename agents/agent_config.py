"""
Configuración centralizada para todos los agentes del grafo LangGraph.

Este módulo contiene los prompts, configuraciones y constantes
que utilizan los diferentes agentes.
"""

# Configuración del agente Niño
NIÑO_AGENT_CONFIG = {
    "name": "niño",
    "age": "8 años",
    "personality": "infantil, con emoción y curiosidad",
    "language_style": "lenguaje simple y expresiones típicas de un niño",
    "base_prompt": "Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño."
}

# Configuración del agente Anciano
ANCIANO_AGENT_CONFIG = {
    "name": "anciano",
    "age": "80 años",
    "personality": "sabio, con experiencia, paciencia y sabiduría",
    "language_style": "tono reflexivo y comparte lecciones de vida cuando sea apropiado",
    "base_prompt": "Eres un anciano sabio de 80 años. Responde con experiencia, paciencia y sabiduría. Usa un tono reflexivo y comparte lecciones de vida cuando sea apropiado."
}

# Configuración del agente de Resumen
SUMMARIZER_AGENT_CONFIG = {
    "name": "summarize_conversation",
    "extend_prompt": "Extiende el resumen teniendo en cuenta los nuevos mensajes arriba:",
    "create_prompt": "Crea un resumen de la conversación arriba:",
    "keep_messages": 2
}

# Configuración del Router
ROUTER_AGENT_CONFIG = {
    "available_agents": ["niño", "anciano"],
    "summary_threshold": 6,  # Número de mensajes antes de resumir
    "default_route": "niño"
}

# Configuración general del grafo
GRAPH_CONFIG = {
    "max_messages_before_summary": 6,
    "summary_keep_messages": 2,
    "default_status": "greeting"
}
