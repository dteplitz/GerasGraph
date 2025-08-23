"""
Clase base para todos los agentes del grafo LangGraph.

Esta clase proporciona funcionalidad común como logging, manejo de errores
y gestión de timestamps para todos los agentes.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any
from log_manager import get_log_manager
from datetime import datetime

class BaseAgent(ABC):
    """Clase base abstracta para todos los agentes"""
    
    def __init__(self, model, agent_name: str):
        """Inicializar el agente base"""
        self.model = model
        self.agent_name = agent_name
        self.log_manager = get_log_manager()
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Método principal que ejecuta el agente con logging automático"""
        start_time = time.time()
        
        try:
            # Log del estado antes de ejecutar
            self.log_manager.log_before_agent(self.agent_name, state)
            
            # Ejecutar la lógica específica del agente
            result = self._process_state(state)
            
            # Asegurar que el resultado tenga timestamp
            if isinstance(result, dict) and "updated_at" not in result:
                result["updated_at"] = datetime.now()
            
            # Extraer la respuesta para el logging
            response_text = self._extract_response_text(result)
            
            # Log del estado después de ejecutar
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent(self.agent_name, result, processing_time, response_text)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error(self.agent_name, e, state)
            raise
    
    @abstractmethod
    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Método abstracto que cada agente debe implementar"""
        pass
    
    def _prepare_prompt_text(self, messages) -> str:
        """Preparar el texto del prompt para logging"""
        return "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    
    def _log_prompt(self, state: Dict[str, Any], prompt_text: str):
        """Log del prompt completo antes de ejecutar"""
        self.log_manager.log_before_agent(self.agent_name, state, prompt_text)
    
    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """Extraer el texto de la respuesta del resultado del agente"""
        try:
            if "messages" in result and result["messages"]:
                # Obtener el último mensaje (que debería ser la respuesta del agente)
                last_message = result["messages"][-1]
                
                # Si es un mensaje de LangChain, extraer el contenido
                if hasattr(last_message, 'content'):
                    return last_message.content
                # Si es un diccionario, buscar el campo content
                elif isinstance(last_message, dict) and 'content' in last_message:
                    return last_message['content']
                # Fallback: convertir a string
                else:
                    return str(last_message)
            
            # Si no hay mensajes, buscar otros campos que puedan contener la respuesta
            for key in ['response', 'answer', 'output', 'result']:
                if key in result:
                    value = result[key]
                    if hasattr(value, 'content'):
                        return value.content
                    elif isinstance(value, str):
                        return value
                    else:
                        return str(value)
            
            # Si no se encuentra nada, retornar un mensaje indicativo
            return "Respuesta no disponible en formato de texto"
            
        except Exception as e:
            return f"Error extrayendo respuesta: {str(e)}"
