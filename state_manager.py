"""
StateManager para manejar todas las modificaciones del estado del grafo LangGraph.

Este módulo proporciona una interfaz centralizada para gestionar el estado
de las conversaciones, incluyendo timestamps, status, y otros campos.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from langchain_core.messages import HumanMessage

# Enum para el status del estado
class ConversationStatus(Enum):
    GREETING = "greeting"
    EXPLORING = "exploring"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"

class StateManager:
    """Manager para manejar todas las modificaciones del estado"""
    
    @staticmethod
    def create_initial_state(user_message: HumanMessage, user: Optional[str] = None) -> Dict[str, Any]:
        """Crear el estado inicial con todos los campos"""
        current_time = datetime.now()
        
        return {
            "messages": [user_message],
            "summary": "",
            "status": ConversationStatus.GREETING,
            "greeted": False,
            "reason": None,
            "question": None,
            "created_at": current_time,
            "updated_at": current_time,
            "user": user
        }
    
    @staticmethod
    def update_timestamp(state: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar el timestamp de updated_at en el estado"""
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def update_status(state: Dict[str, Any], new_status: ConversationStatus) -> Dict[str, Any]:
        """Actualizar el status de la conversación"""
        state["status"] = new_status
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def set_greeted(state: Dict[str, Any], greeted: bool = True) -> Dict[str, Any]:
        """Marcar que se ha saludado al usuario"""
        state["greeted"] = greeted
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def set_reason(state: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Establecer la razón de la conversación"""
        state["reason"] = reason
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def set_question(state: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Establecer la pregunta actual"""
        state["question"] = question
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def add_message(state: Dict[str, Any], message) -> Dict[str, Any]:
        """Agregar un mensaje al estado"""
        state["messages"].append(message)
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def update_summary(state: Dict[str, Any], new_summary: str) -> Dict[str, Any]:
        """Actualizar el resumen de la conversación"""
        state["summary"] = new_summary
        state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def remove_old_messages(state: Dict[str, Any], keep_count: int = 2) -> Dict[str, Any]:
        """Eliminar mensajes antiguos, manteniendo solo los más recientes"""
        if len(state["messages"]) > keep_count:
            state["messages"] = state["messages"][-keep_count:]
            state["updated_at"] = datetime.now()
        return state
    
    @staticmethod
    def get_state_info(state: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información resumida del estado para logging"""
        return {
            "status": state.get("status", "unknown"),
            "greeted": state.get("greeted", False),
            "reason": state.get("reason"),
            "question": state.get("question"),
            "user": state.get("user"),
            "message_count": len(state.get("messages", [])),
            "has_summary": bool(state.get("summary")),
            "created_at": state.get("created_at"),
            "updated_at": state.get("updated_at")
        }
