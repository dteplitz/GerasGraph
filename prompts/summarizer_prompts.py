"""
Prompts para el agente Summarizer del sistema GerasGraph.

Este módulo contiene todos los prompts específicos para el agente Summarizer,
que se encarga de crear y extender resúmenes de las conversaciones.
"""

# Configuración del agente de Resumen
SUMMARIZER_AGENT_CONFIG = {
    "name": "summarize_conversation",
    "extend_prompt": "Extiende el resumen teniendo en cuenta los nuevos mensajes arriba:",
    "create_prompt": "Crea un resumen de la conversación arriba:",
    "keep_messages": 2
}

# Prompt para extender un resumen existente
SUMMARY_EXTEND_PROMPT = "Extiende el resumen teniendo en cuenta los nuevos mensajes arriba:"

# Prompt para crear un nuevo resumen
SUMMARY_CREATE_PROMPT = "Crea un resumen de la conversación arriba:"

# Prompt completo para extender resumen con contexto
SUMMARY_EXTEND_WITH_CONTEXT = "Este es el resumen de la conversación hasta ahora: {summary}\n\n{extend_prompt}"
