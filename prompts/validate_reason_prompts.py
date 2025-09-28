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

# Prompts específicos para cada tipo de objetivo
REASON_DETECTION_OBJETIVO_MONTO_FINAL = """Analiza si el usuario ha especificado un monto final objetivo válido.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "MONTO"}} donde MONTO es el valor numérico exacto que mencionó el usuario
{{"has_response": 0, "reason": null}} si la respuesta es vaga o no especifica un monto

## CRITERIOS PARA RESPUESTA VÁLIDA (has_response: 1):
✅ Extraer el monto exacto mencionado:
- "10 millones" → {{"has_response": 1, "reason": "10000000"}}
- "5000000 pesos" → {{"has_response": 1, "reason": "5000000"}}
- "1M" → {{"has_response": 1, "reason": "1000000"}}
- "USD 50000" → {{"has_response": 1, "reason": "50000"}}
- "10M en 20 años" → {{"has_response": 1, "reason": "10000000"}}

## CRITERIOS PARA RESPUESTA INVÁLIDA (has_response: 0):
❌ Montos vagos: "mucho dinero", "bastante plata"
❌ Sin montos: "lo que pueda", "veremos"
❌ Respuestas genéricas: "ok", "bien", "después veo"

NOTA: Siempre devolver el monto como número sin símbolos de moneda ni puntos/comas.

RESPUESTA:"""

REASON_DETECTION_OBJETIVO_RENTA = """Analiza si el usuario ha especificado un monto de renta mensual válido.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "MONTO"}} donde MONTO es el valor numérico mensual exacto que mencionó el usuario
{{"has_response": 0, "reason": null}} si la respuesta es vaga o no especifica un monto

## CRITERIOS PARA RESPUESTA VÁLIDA (has_response: 1):
✅ Extraer el monto mensual exacto:
- "300000 por mes" → {{"has_response": 1, "reason": "300000"}}
- "5000 mensuales" → {{"has_response": 1, "reason": "5000"}}
- "USD 2000 mensuales" → {{"has_response": 1, "reason": "2000"}}
- "60000 anuales" → {{"has_response": 1, "reason": "5000"}} (dividir entre 12)
- "3000 dólares al mes" → {{"has_response": 1, "reason": "3000"}}

## CRITERIOS PARA RESPUESTA INVÁLIDA (has_response: 0):
❌ Montos vagos: "un buen sueldo", "lo suficiente"
❌ Sin periodicidad clara: "5000" (sin especificar si es mensual)
❌ Respuestas genéricas: "ok", "bien", "después veo"

NOTA: 
1. Siempre devolver el monto como número sin símbolos de moneda ni puntos/comas
2. Si el monto es anual, dividirlo entre 12 para obtener el valor mensual

RESPUESTA:"""

REASON_DETECTION_OBJETIVO_DURACION = """Analiza si el usuario ha especificado una duración válida.

PREGUNTA: {current_question}

RESPUESTA DEL USUARIO: {user_message}

INSTRUCCIÓN: Responde ÚNICAMENTE con un JSON en este formato exacto:
{{"has_response": 1, "reason": "AÑOS"}} donde AÑOS es el número de años especificado por el usuario
{{"has_response": 0, "reason": null}} si la respuesta es vaga o no especifica un plazo

## CRITERIOS PARA RESPUESTA VÁLIDA (has_response: 1):
✅ Extraer el número exacto de años:
- "20 años" → {{"has_response": 1, "reason": "20"}}
- "una década" → {{"has_response": 1, "reason": "10"}}
- "hasta 2040" → {{"has_response": 1, "reason": "16"}} (calcular años desde 2024)
- "invertir 10 años" → {{"has_response": 1, "reason": "10"}}
- "ahorrar por 5 años" → {{"has_response": 1, "reason": "5"}}
- "para cuando tenga 65" → calcular basado en la edad actual si está disponible

## CRITERIOS PARA RESPUESTA INVÁLIDA (has_response: 0):
❌ Plazos vagos: "largo plazo", "varios años"
❌ Sin tiempo específico: "cuando pueda", "más adelante"
❌ Respuestas genéricas: "ok", "bien", "después veo"

NOTA:
1. Siempre devolver el número de años como un número entero sin texto adicional
2. Para fechas futuras (ej: "hasta 2040"), calcular la diferencia de años desde 2024
3. Para edades objetivo, usar la edad actual del usuario si está disponible, sino devolver has_response: 0

RESPUESTA:"""

# Mapeo simple por tipo de pregunta (enum string) → prompt específico
REASON_DETECTION_BY_TYPE = {
    "tipo_objetivo": REASON_DETECTION_TIPO_OBJETIVO_PROMPT,
    "objetivo_monto_final": REASON_DETECTION_OBJETIVO_MONTO_FINAL,
    "objetivo_renta": REASON_DETECTION_OBJETIVO_RENTA,
    "objetivo_duracion": REASON_DETECTION_OBJETIVO_DURACION,
    "monto_inicial": GENERIC_REASON_DETECTION_PROMPT,
    "aporte_mensual": GENERIC_REASON_DETECTION_PROMPT
}
