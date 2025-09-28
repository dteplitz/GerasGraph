"""
Prompts para el agente ValidateReason.

Este módulo contiene todos los prompts utilizados por el ValidateReasonAgent
para detectar si hay una razón explícita en la respuesta del usuario
y determinar el flujo inicial de la conversación.
"""

GENERIC_REASON_DETECTION_PROMPT = """Analiza si el usuario ha respondido a la pregunta.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "respuesta concreta del usuario"}} si la respuesta contesta claramente la pregunta
{{"has_response": 0, "reason": null}} si la respuesta es vaga, incompleta o no contesta

CRITERIOS (has_response: 1): la respuesta contiene datos o una elección explícita relevante a la pregunta.
CRITERIOS (has_response: 0): expresiones vagas ("no sé", "tengo dudas", "después veo", "ok"), o no hay elección/dato concreto.

RESPUESTA:"""

REASON_DETECTION_TIPO_OBJETIVO_PROMPT = """Analiza si el usuario ha respondido a la pregunta.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "Monto final"}} si el usuario elige la opción de monto final
{{"has_response": 1, "reason": "Renta"}} si el usuario elige la opción de renta
{{"has_response": 1, "reason": "Duración"}} si el usuario elige la opción de duración
{{"has_response": 0, "reason": null}} si el usuario NO eligió una opción específica

## CRITERIOS PARA RESPUESTA VÁLIDA (has_response: 1):
✅ El usuario elige EXPLÍCITAMENTE una de las tres opciones:
- "Monto final" → cuando menciona monto final, monto objetivo, cantidad final, dinero acumulado, etc.
- "Renta" → cuando menciona renta, ingreso mensual, cobrar por mes, etc.
- "Duración" → cuando menciona duración, tiempo de inversión, plazo, años, etc.

## CRITERIOS PARA RESPUESTA INVÁLIDA (has_response: 0):
❌ Respuestas vagas: "dudas", "no sé", "ni idea", "uh"
❌ Respuestas genéricas: "ok", "bien", "gracias"
❌ Expresiones de confusión: "tengo dudas", "estoy confundido"
❌ Respuestas que no eligen una opción específica

RESPUESTA:"""

# Mapeo simple por tipo de pregunta (enum string) → prompt específico
REASON_DETECTION_BY_TYPE = {
    "tipo_objetivo": REASON_DETECTION_TIPO_OBJETIVO_PROMPT,
    "objetivo": GENERIC_REASON_DETECTION_PROMPT,
    "monto_inicial": GENERIC_REASON_DETECTION_PROMPT,
    "aporte_mensual": GENERIC_REASON_DETECTION_PROMPT
}
