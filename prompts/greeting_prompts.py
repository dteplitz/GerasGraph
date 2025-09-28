"""
Prompts para el sistema de saludo del sistema GerasGraph.

Este módulo contiene los prompts relacionados con el saludo inicial
y la bienvenida al usuario.
"""

"""
Prompts para saludo dinámico que referencia la pregunta actual de la sesión.
"""

# Mapeo directo: tipo de pregunta (usar valores de QuestionType) → saludo/pregunta a mostrar
from custom_types import QuestionType

GREETING_BY_TYPE = {
    # tipo_objetivo: saludo largo + pregunta corta
    QuestionType.TIPO_OBJETIVO.value: {
        "greeting": (
            "¡Hola! Vamos a comenzar a armar plan de retiro.\n"
            "Lo primero es elegir tu tipo de plan. Tenés tres opciones:\n\n"
            "Monto final → definís cuánto dinero querés tener acumulado al final del plazo. Ej: \"quiero llegar a 10 millones en 20 años\".\n\n"
            "Renta → pensás en términos de ingresos mensuales cuando ya no trabajes. Ej: \"quiero cobrar 300.000 pesos por mes\".\n\n"
            "Duración → elegís el tiempo que querés invertir (por ejemplo 15 años) y vemos cuánto podrías acumular según lo que aportes.\n\n"
            "Elegí la opción que más se parezca a cómo imaginás tu futuro. No te preocupes, después vas a poder modificar todo lo que quieras.\n\n"
            "Y si no lo tenés del todo claro, podés preguntarme lo que quieras — estoy acá para ayudarte a decidir."
        ),
        "question": "¿Qué tipo de plan te gustaría elegir? Podés elegir Monto final, Renta o Duración."
    },
    # Placeholders simples para personalizar fácilmente
    # Variantes específicas de OBJETIVO_*
    QuestionType.OBJETIVO_MONTO_FINAL.value: {
        "greeting": (
            "Perfecto, trabajemos con Monto final.\n"
            "Decime a cuánto querés llegar al final del período (por ej.: 10 millones, 50.000 USD)."
        ),
        "question": "¿Cuál es tu monto final objetivo?"
    },
    QuestionType.OBJETIVO_RENTA.value: {
        "greeting": (
            "Genial, trabajemos con Renta.\n"
            "Contame qué ingreso mensual te gustaría recibir (por ej.: 300.000 pesos/mes, 1.000 USD mensuales)."
        ),
        "question": "¿Qué ingreso mensual te gustaría recibir?"
    },
    QuestionType.OBJETIVO_DURACION.value: {
        "greeting": (
            "Vamos con Duración.\n"
            "Indicá por cuántos años o meses querés sostener el plan (por ej.: 15 años, 180 meses)."
        ),
        "question": "¿Por cuántos años o meses querés sostener el plan?"
    },
    # Preguntas sobre montos
    QuestionType.MONTO_INICIAL.value: {
        "greeting": (
            "Ahora necesito saber con qué monto inicial contás para arrancar.\n"
            "Puede ser cualquier valor, incluso cero si arrancás de cero.\n"
            "Por ejemplo: 100.000 pesos, 1M, 500K, USD 5000, o simplemente 0 si no tenés monto inicial."
        ),
        "question": "¿Con qué monto inicial contás para empezar?"
    },
    QuestionType.APORTE_MENSUAL.value: {
        "greeting": (
            "¿Cuánto podrías aportar mensualmente al plan?\n"
            "Pensá en un monto que puedas mantener de forma constante.\n"
            "Por ejemplo: 50.000 por mes, 1000 USD mensuales, o si preferís podés decirme un monto anual y lo dividimos en 12."
        ),
        "question": "¿Cuánto podés aportar por mes?"
    }
}

# Mensaje de bienvenida legacy (por compatibilidad)
GREETING_MESSAGE = GREETING_BY_TYPE[QuestionType.TIPO_OBJETIVO.value]["greeting"]
# Mensaje de bienvenida inicial
#GREETING_MESSAGE = """¡Hola! Vamos a comenzar a armar plan de retiro.
#Lo primero es elegir tu tipo de plan. Tenés tres opciones:

#Monto final → definís cuánto dinero querés tener acumulado al final del plazo. Ej: "quiero llegar a 10 millones en 20 años".

#Renta → pensás en términos de ingresos mensuales cuando ya no trabajes. Ej: "quiero cobrar 300.000 pesos por mes".

#Duración → elegís el tiempo que querés invertir (por ejemplo 15 años) y vemos cuánto podrías acumular según lo que aportes.

#Elegí la opción que más se parezca a cómo imaginás tu futuro. No te preocupes, después vas a poder modificar todo lo que quieras.

#Y si no lo tenés del todo claro, podés preguntarme lo que quieras — estoy acá para ayudarte a decidir."""

