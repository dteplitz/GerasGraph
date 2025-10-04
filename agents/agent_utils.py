"""
Utilidades comunes para todos los agentes del grafo LangGraph.

Este módulo contiene funciones auxiliares que pueden ser utilizadas
por diferentes agentes.
"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage

def build_system_prompt(base_prompt: str, summary: str = None) -> str:
    """
    Construir el prompt del sistema con contexto del resumen si existe.
    
    Args:
        base_prompt: Prompt base del agente
        summary: Resumen de la conversación anterior (opcional)
    
    Returns:
        Prompt completo del sistema
    """
    if summary and summary.strip():
        return f"{base_prompt}\n\nResumen de la conversación anterior: {summary}"
    return base_prompt

def format_messages_for_logging(messages: List[BaseMessage]) -> str:
    """
    Formatear mensajes para logging legible.
    
    Args:
        messages: Lista de mensajes de LangChain
    
    Returns:
        String formateado de los mensajes
    """
    return "\n".join([f"{msg.type}: {msg.content}" for msg in messages])

def extract_text_from_content(content: Any) -> str:
    """Extrae texto de content que puede ser str, dict o lista de bloques.
    
    Args:
        content: Contenido que puede ser string, dict o lista de bloques
        
    Returns:
        Texto extraído y concatenado
    """
    try:
        # Caso simple: string
        if isinstance(content, str):
            return content
        # Caso dict (p. ej. {"type": "text", "text": "..."})
        if isinstance(content, dict):
            if "text" in content and isinstance(content["text"], str):
                return content["text"]
            # Fallback a stringify
            return str(content)
        # Caso lista de bloques (RAG/tool events + text)
        if isinstance(content, list):
            text_parts: list[str] = []
            for block in content:
                # Bloques como {"type": "text", "text": "..."}
                if isinstance(block, dict):
                    block_type = block.get("type")
                    if block_type == "text" and isinstance(block.get("text"), str):
                        text_parts.append(block["text"])
                    # Algunos providers usan {"text": "..."} sin type
                    elif "text" in block and isinstance(block.get("text"), str):
                        text_parts.append(block["text"])
                    # Ignorar tool_use, tool_result, file_search_call, etc.
                elif isinstance(block, str):
                    text_parts.append(block)
            return "\n\n".join([p for p in text_parts if p]) or str(content)
        # Fallback genérico
        return str(content)
    except Exception:
        return str(content)

def extract_response_content(response) -> str:
    """
    Extraer el contenido de la respuesta del modelo de forma segura.
    
    Args:
        response: Respuesta del modelo LLM
    
    Returns:
        Contenido de la respuesta como string
    """
    if hasattr(response, 'content'):
        return extract_text_from_content(response.content)
    elif isinstance(response, str):
        return response
    elif isinstance(response, dict) and 'content' in response:
        return extract_text_from_content(response['content'])
    else:
        return str(response)

def validate_state_fields(state: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validar que el estado tenga todos los campos requeridos.
    
    Args:
        state: Estado a validar
        required_fields: Lista de campos requeridos
    
    Returns:
        True si todos los campos están presentes
    """
    return all(field in state for field in required_fields)

def get_state_summary(state: Dict[str, Any]) -> str:
    """
    Obtener el resumen del estado de forma segura.
    
    Args:
        state: Estado del grafo
    
    Returns:
        Resumen de la conversación o string vacío
    """
    return state.get("summary", "").strip()

def count_messages(state: Dict[str, Any]) -> int:
    """
    Contar el número de mensajes en el estado de forma segura.
    
    Args:
        state: Estado del grafo
    
    Returns:
        Número de mensajes
    """
    messages = state.get("messages", [])
    return len(messages) if isinstance(messages, list) else 0
