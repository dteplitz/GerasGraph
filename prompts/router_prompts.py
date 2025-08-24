"""
Prompts para el agente router mejorado.

Este módulo contiene todos los prompts utilizados por el RouterAgent
para detectar si hay una razón explícita en la respuesta del usuario
y determinar el flujo de la conversación.
"""

REASON_DETECTION_PROMPT = """Analiza si el usuario ha respondido a la pregunta.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "la razón específica o elección del usuario"}} si el usuario dio una respuesta a la pregunta
{{"has_response": 0, "reason": null}} si el usuario NO dio una respuesta a la pregunta

IMPORTANTE: En el campo "reason" pon SOLO la razón o elección del usuario, NO describas lo que hizo. 
Ejemplos:
- Si dice "Prefiero renta fija" → "reason": "renta fija"
- Si dice "Me gusta el monto final" → "reason": "monto final"
- Si dice "Tengo dudas sobre la duración" → "reason": "dudas sobre duración"

RESPUESTA:"""


