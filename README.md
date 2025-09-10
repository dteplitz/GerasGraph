# Agente LangGraph con Groq

Un proyecto base de LangGraph que implementa un agente conversacional simple que se comunica con la API de Groq.

## Características

- **1 Agente**: Un agente conversacional básico
- **Router**: Nodo que decide aleatoriamente qué agente responde
- **Checkpoints con SQLite**: Memoria persistente usando base de datos SQLite
- **API FastAPI**: Interfaz HTTP para comunicarse con el agente
- **Sin herramientas**: Implementación mínima sin herramientas externas

## Estructura del Grafo

```
START → ValidateReason → StateDecision → [Confirmation | EndConversation | Profesor] → END
```

- **ValidateReason**: Valida si el usuario dio una razón válida
- **StateDecision**: Decide el siguiente paso basado en el estado
- **Confirmation**: Pide confirmación de la elección del usuario
- **EndConversation**: Maneja el final de la conversación
- **Profesor**: Continúa explorando opciones con el usuario

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar API Key de Groq:
   - Obtén tu API key en [https://console.groq.com/](https://console.groq.com/)
   - El programa te pedirá la key al ejecutarlo
   - O configura variables de entorno (ver `env.example`)

## Uso

Ejecutar la API FastAPI:
```bash
python api.py
```

### Uso de la API:
- **POST** `/chat` - Enviar mensaje y recibir respuesta
- **GET** `/health` - Verificar estado de la API
- **GET** `/` - Información básica de la API

## Memoria

El agente mantiene memoria de la conversación usando:
- **SQLite**: Base de datos local para persistencia
- **Checkpoints**: Estado del grafo se guarda automáticamente
- **Thread ID**: Cada sesión tiene un identificador único

## Personalización

Para modificar el comportamiento:

1. **Agregar nuevos nodos**: Crear funciones y agregarlas al grafo
2. **Modificar routing**: Cambiar la lógica en `route_to_next()`
3. **Cambiar modelo**: Modificar `init_model()` para usar otros modelos de Groq
4. **Extender estado**: Agregar campos al `State` TypedDict

## Dependencias Principales

- `langgraph`: Framework principal para crear grafos de agentes
- `langchain-groq`: Integración con la API de Groq
- `langgraph-checkpoint-sqlite`: Persistencia con SQLite
- `langchain-core`: Componentes base de LangChain
- `fastapi`: Framework web para la API
- `uvicorn`: Servidor ASGI para FastAPI

## Próximos Pasos

- [ ] Agregar herramientas (tools)
- [ ] Implementar manejo de errores
- [ ] Agregar logging y monitoreo
- [ ] Crear interfaz web
- [ ] Agregar más nodos especializados

