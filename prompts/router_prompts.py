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
{{"has_response": 1, "reason": "la elección específica del usuario"}} si el usuario eligió UNA de las tres opciones
{{"has_response": 0, "reason": null}} si el usuario NO eligió una opción específica

## CRITERIOS PARA RESPUESTA VÁLIDA (has_response: 1):
✅ El usuario elige EXPLÍCITAMENTE una de las tres opciones:
- "Monto final" o "prefiero monto final" o "quiero monto final"
- "Renta" o "prefiero renta" o "quiero renta" 
- "Duración" o "prefiero duración" o "quiero duración"

## CRITERIOS PARA RESPUESTA INVÁLIDA (has_response: 0):
❌ Respuestas vagas: "dudas", "no sé", "ni idea", "uh"
❌ Respuestas genéricas: "ok", "bien", "gracias"
❌ Expresiones de confusión: "tengo dudas", "estoy confundido"
❌ Respuestas que no eligen una opción específica

## EJEMPLOS:
- "Prefiero el plan de monto final" → has_response: 1, reason: "monto final"
- "Me gusta la renta" → has_response: 1, reason: "renta"
- "Eligo duración" → has_response: 1, reason: "duración"
- "Dudas" → has_response: 0, reason: null
- "Tengo dudas sobre la duración" → has_response: 0, reason: null
- "No sé qué elegir" → has_response: 0, reason: null

RESPUESTA:"""


