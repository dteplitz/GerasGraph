# Arquitectura del Proyecto GerasGraph

## Visión General

GerasGraph es un sistema de conversación basado en LangGraph que utiliza múltiples agentes especializados para mantener conversaciones dinámicas y contextuales.

## Estructura de Archivos

```
GerasGraph/
├── agents/                          # Paquete de agentes especializados
│   ├── __init__.py                 # Exportaciones del paquete
│   ├── base_agent.py               # Clase base para todos los agentes
│   ├── niño_agent.py               # Agente que responde como un niño
│   ├── anciano_agent.py            # Agente que responde como un anciano
│   ├── summarizer_agent.py         # Agente que resume conversaciones
│   ├── router_agent.py             # Agente que decide el flujo
│   ├── agent_config.py             # Configuraciones centralizadas
│   └── agent_utils.py              # Utilidades comunes
├── state_manager.py                 # Gestión centralizada del estado
├── log_manager.py                   # Sistema de logging
├── graph_interface.py               # Interfaz principal del grafo
├── types.py                         # Definiciones de tipos
├── config.py                        # Configuración del proyecto
├── main.py                          # Punto de entrada
└── README.md                        # Documentación principal
```

## Componentes Principales

### 1. StateManager (`state_manager.py`)

**Responsabilidad**: Gestionar todas las modificaciones del estado del grafo.

**Características**:
- Creación de estado inicial
- Actualización de timestamps
- Gestión de campos del estado (status, greeted, reason, question)
- Validación de estado

**Uso**:
```python
from state_manager import StateManager

state_manager = StateManager()
initial_state = state_manager.create_initial_state(user_message, user)
updated_state = state_manager.update_status(state, ConversationStatus.EXPLORING)
```

### 2. BaseAgent (`agents/base_agent.py`)

**Responsabilidad**: Proporcionar funcionalidad común para todos los agentes.

**Características**:
- Logging automático (antes/después/errores)
- Manejo de timestamps
- Gestión de errores
- Métodos de utilidad comunes

**Uso**:
```python
from agents import BaseAgent

class MiAgente(BaseAgent):
    def __init__(self, model):
        super().__init__(model, "mi_agente")
    
    def _process_state(self, state):
        # Lógica específica del agente
        return {"messages": [response]}
```

### 3. Agentes Especializados

#### NiñoAgent
- **Persona**: Niño de 8 años
- **Estilo**: Infantil, emocional, curioso
- **Lenguaje**: Simple, expresivo

#### AncianoAgent
- **Persona**: Anciano sabio de 80 años
- **Estilo**: Experto, paciente, reflexivo
- **Lenguaje**: Sabio, con lecciones de vida

#### SummarizerAgent
- **Función**: Crear y extender resúmenes
- **Lógica**: Mantener solo los 2 mensajes más recientes
- **Trigger**: Después de 6 mensajes

#### RouterAgent
- **Función**: Decidir el flujo de la conversación
- **Lógica**: Selección aleatoria entre agentes
- **Decisiones**: Cuándo resumir vs. continuar

### 4. Sistema de Logging (`log_manager.py`)

**Responsabilidad**: Registrar todas las actividades del grafo.

**Características**:
- Logging antes/después de cada agente
- Captura de prompts y respuestas completas
- Múltiples observadores (consola, archivo)
- Formato estructurado (JSONL)

### 5. GraphInterface (`graph_interface.py`)

**Responsabilidad**: Coordinar todos los componentes del grafo.

**Características**:
- Patrón Singleton
- Inicialización de agentes
- Creación y compilación del grafo
- Interfaz pública para procesar mensajes

## Flujo de Datos

```
Usuario → GraphInterface → RouterAgent → [NiñoAgent | AncianoAgent] → RouterAgent → [Continuar | SummarizerAgent]
```

1. **Entrada**: Usuario envía mensaje
2. **Inicialización**: StateManager crea estado inicial
3. **Routing**: RouterAgent selecciona agente aleatoriamente
4. **Procesamiento**: Agente seleccionado procesa el mensaje
5. **Decisión**: RouterAgent decide si continuar o resumir
6. **Salida**: Respuesta del agente o resumen de la conversación

## Estado del Grafo

### Campos del Estado
- **`messages`**: Lista de mensajes de la conversación
- **`summary`**: Resumen acumulativo de la conversación
- **`status`**: Estado actual (greeting, exploring, waiting_confirmation, completed)
- **`greeted`**: Boolean indicando si se saludó al usuario
- **`reason`**: Razón de la conversación
- **`question`**: Pregunta actual
- **`created_at`**: Timestamp de creación
- **`updated_at`**: Timestamp de última actualización
- **`user`**: Identificador del usuario

## Configuración

### Archivos de Configuración
- **`agent_config.py`**: Configuraciones específicas de cada agente
- **`config.py`**: Configuración general del proyecto (modelos, base de datos)
- **`types.py`**: Definiciones de tipos para mejor tipado

## Beneficios de la Arquitectura

### 1. **Separación de Responsabilidades**
- Cada componente tiene una responsabilidad específica
- Fácil identificar dónde hacer cambios

### 2. **Reutilización**
- BaseAgent proporciona funcionalidad común
- Utilidades compartidas entre agentes

### 3. **Mantenibilidad**
- Código organizado y estructurado
- Fácil agregar nuevos agentes
- Configuración centralizada

### 4. **Testabilidad**
- Cada componente se puede testear independientemente
- Fácil hacer mock de dependencias

### 5. **Extensibilidad**
- Arquitectura preparada para nuevos agentes
- Sistema de logging extensible
- Estado flexible para nuevos campos

## Agregar Nuevos Agentes

1. **Crear clase del agente** heredando de `BaseAgent`
2. **Implementar método** `_process_state()`
3. **Agregar configuración** en `agent_config.py`
4. **Actualizar RouterAgent** si es necesario
5. **Registrar en GraphInterface**

## Mejores Prácticas

1. **Siempre heredar de BaseAgent** para nuevos agentes
2. **Usar las utilidades** de `agent_utils.py`
3. **Configurar en agent_config.py** en lugar de hardcodear
4. **Manejar errores** apropiadamente
5. **Documentar** cambios en la arquitectura
