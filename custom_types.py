"""
Definiciones de tipos para el proyecto GerasGraph.

Este módulo centraliza todos los tipos personalizados utilizados
en el proyecto para mejor mantenibilidad y consistencia.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState

# Tipo para el estado del grafo
State = MessagesState

# Tipo para respuestas de agentes
AgentResponse = Dict[str, Any]

# Tipo para configuraciones de agentes
AgentConfig = Dict[str, Any]

# Tipo para mensajes del sistema
SystemPrompt = str

# Tipo para identificadores de usuario
UserID = str

# Tipo para identificadores de sesión
SessionID = str

# Tipo para timestamps
Timestamp = datetime

# Tipo para resúmenes
Summary = str

# Tipo para razones de conversación
ConversationReason = Optional[str]

# Tipo para preguntas
Question = Optional[str]

# Tipo para status de conversación
ConversationStatus = str

# Tipo para respuestas del LLM
LLMResponse = Union[AIMessage, str, Dict[str, Any]]

# Tipo para prompts
Prompt = Union[str, List[BaseMessage]]

# Tipo para resultados de agentes
AgentResult = Dict[str, Any]

# Tipo para configuraciones del grafo
GraphConfig = Dict[str, Any]

# Tipo para logs
LogEntry = Dict[str, Any]

# Tipo para errores
ErrorInfo = Dict[str, Any]
