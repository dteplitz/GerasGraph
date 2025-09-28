"""
Prompts para el sistema de saludo del sistema GerasGraph.

Este módulo contiene los prompts relacionados con el saludo inicial
y la bienvenida al usuario.
"""

"""
Prompts para saludo dinámico que referencia la pregunta actual de la sesión.
"""

# Mapeo directo: tipo de pregunta (enum string) → saludo/pregunta a mostrar
GREETING_BY_TYPE = {
    # tipo_objetivo: usar el mensaje largo provisto
    "tipo_objetivo": (
        "¡Hola! Vamos a comenzar a armar plan de retiro.\n"
        "Lo primero es elegir tu tipo de plan. Tenés tres opciones:\n\n"
        "Monto final → definís cuánto dinero querés tener acumulado al final del plazo. Ej: \"quiero llegar a 10 millones en 20 años\".\n\n"
        "Renta → pensás en términos de ingresos mensuales cuando ya no trabajes. Ej: \"quiero cobrar 300.000 pesos por mes\".\n\n"
        "Duración → elegís el tiempo que querés invertir (por ejemplo 15 años) y vemos cuánto podrías acumular según lo que aportes.\n\n"
        "Elegí la opción que más se parezca a cómo imaginás tu futuro. No te preocupes, después vas a poder modificar todo lo que quieras.\n\n"
        "Y si no lo tenés del todo claro, podés preguntarme lo que quieras — estoy acá para ayudarte a decidir."
    ),
    # Placeholders simples para personalizar fácilmente
    "objetivo": "¿Cuál es tu objetivo específico?",
    "monto_inicial": "¿Con qué monto inicial contás?",
    "aporte_mensual": "¿Cuánto podés aportar por mes?"
}

# Mensaje de bienvenida legacy (por compatibilidad)
GREETING_MESSAGE = GREETING_BY_TYPE["tipo_objetivo"]
# Mensaje de bienvenida inicial
#GREETING_MESSAGE = """¡Hola! Vamos a comenzar a armar plan de retiro.
#Lo primero es elegir tu tipo de plan. Tenés tres opciones:

#Monto final → definís cuánto dinero querés tener acumulado al final del plazo. Ej: "quiero llegar a 10 millones en 20 años".

#Renta → pensás en términos de ingresos mensuales cuando ya no trabajes. Ej: "quiero cobrar 300.000 pesos por mes".

#Duración → elegís el tiempo que querés invertir (por ejemplo 15 años) y vemos cuánto podrías acumular según lo que aportes.

#Elegí la opción que más se parezca a cómo imaginás tu futuro. No te preocupes, después vas a poder modificar todo lo que quieras.

#Y si no lo tenés del todo claro, podés preguntarme lo que quieras — estoy acá para ayudarte a decidir."""

