"""
LogManager centralizado para logging del estado del grafo LangGraph.

Este módulo proporciona logging detallado del estado antes y después
de cada agente del grafo, usando el patrón Observer.
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Niveles de logging disponibles"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class StateChangeEvent:
    """Evento de cambio de estado en el grafo"""
    
    def __init__(self, agent_name: str, event_type: str, state: Dict[str, Any], 
                 timestamp: datetime, processing_time: Optional[float] = None,
                 prompt: Optional[str] = None, response: Optional[str] = None):
        self.agent_name = agent_name
        self.event_type = event_type  # "BEFORE" o "AFTER"
        self.state = state
        self.timestamp = timestamp
        self.processing_time = processing_time
        self.prompt = prompt
        self.response = response


class LogObserver:
    """Interfaz para observadores de logging"""
    
    def on_state_change(self, event: StateChangeEvent):
        """Manejar cambio de estado"""
        pass


class ConsoleLogObserver(LogObserver):
    """Observador que loguea a consola"""
    
    def __init__(self, log_level: LogLevel = LogLevel.INFO):
        self.log_level = log_level
    
    def on_state_change(self, event: StateChangeEvent):
        """Log a consola con formato visual"""
        if event.event_type == "BEFORE":
            print(f"\n{'='*80}")
            print(f"🚀 AGENTE [{event.agent_name.upper()}] - INICIANDO")
            print(f"📅 Timestamp: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            print(f"📊 Estado de entrada:")
            self._log_state(event.state)
            
            # Log del prompt si está disponible
            if event.prompt:
                print(f"📝 PROMPT COMPLETO:")
                print(f"   {event.prompt}")
                
        else:  # AFTER
            print(f"\n✅ AGENTE [{event.agent_name.upper()}] - COMPLETADO")
            if event.processing_time:
                print(f"⏱️ Tiempo de procesamiento: {event.processing_time:.3f}s")
            print(f"📊 Estado de salida:")
            self._log_state(event.state)
            
            # Log de la respuesta si está disponible
            if event.response:
                print(f"🤖 RESPUESTA COMPLETA:")
                print(f"   {event.response}")
                
            print(f"{'='*80}\n")
    
    def _log_state(self, state: Dict[str, Any]):
        """Log del estado de manera legible"""
        if "messages" in state:
            messages = state["messages"]
            print(f"   💬 Mensajes ({len(messages)}):")
            for i, msg in enumerate(messages[-3:], 1):  # Solo últimos 3 mensajes
                if hasattr(msg, 'content'):
                    content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    print(f"      {i}. {content}")
        
        # Log de otros campos del estado
        other_fields = {k: v for k, v in state.items() if k != "messages"}
        if other_fields:
            print(f"   🔧 Otros campos: {json.dumps(other_fields, indent=6, ensure_ascii=False)}")


class FileLogObserver(LogObserver):
    """Observador que loguea a archivo"""
    
    def __init__(self, filename: str = "graph_logs.jsonl", log_level: LogLevel = LogLevel.INFO):
        self.filename = filename
        self.log_level = log_level
    
    def on_state_change(self, event: StateChangeEvent):
        """Log a archivo en formato JSONL"""
        # Convertir el estado a un formato serializable
        serializable_state = self._make_serializable(event.state)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "agent_name": event.agent_name,
            "event_type": event.event_type,
            "processing_time": event.processing_time,
            "prompt": event.prompt,
            "response": event.response,
            "state": serializable_state
        }
        
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ Error escribiendo log a archivo: {e}")
    
    def _make_serializable(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertir el estado a un formato JSON serializable usando métodos oficiales de LangChain.
        
        Esta implementación usa los métodos de serialización nativos de LangChain y Pydantic
        para garantizar la máxima compatibilidad y preservación de metadatos.
        """
        serializable_state = {}
        
        for key, value in state.items():
            if key == "messages":
                # Convertir mensajes de LangChain usando métodos oficiales
                serializable_messages = []
                for msg in value:
                    serializable_msg = self._serialize_langchain_message(msg)
                    serializable_messages.append(serializable_msg)
                serializable_state[key] = serializable_messages
            else:
                # Para otros campos, usar serialización inteligente
                serializable_state[key] = self._serialize_value(value)
        
        return serializable_state
    
    def _serialize_langchain_message(self, message) -> Dict[str, Any]:
        """
        Serializar un mensaje de LangChain usando métodos oficiales.
        
        Prioriza los métodos de serialización nativos de LangChain y Pydantic
        para garantizar la máxima compatibilidad.
        """
        try:
            # Intentar usar model_dump() (Pydantic v2)
            if hasattr(message, 'model_dump'):
                return message.model_dump()
            
            # Intentar usar dict() (Pydantic v1)
            elif hasattr(message, 'dict'):
                return message.dict()
            
            # Intentar usar to_dict() (método legacy)
            elif hasattr(message, 'to_dict'):
                return message.to_dict()
            
            # Fallback: extraer atributos manualmente
            else:
                return self._extract_message_attributes(message)
                
        except Exception as e:
            # Si falla la serialización oficial, usar extracción manual
            print(f"⚠️ Fallback serialization for message: {e}")
            return self._extract_message_attributes(message)
    
    def _extract_message_attributes(self, message) -> Dict[str, Any]:
        """
        Extraer atributos de un mensaje de LangChain de forma manual.
        
        Este método se usa como fallback cuando los métodos oficiales fallan.
        """
        message_data = {
            "type": type(message).__name__,
            "content": getattr(message, 'content', str(message)),
            "additional_kwargs": getattr(message, 'additional_kwargs', {}),
            "response_metadata": getattr(message, 'response_metadata', {}),
            "id": getattr(message, 'id', None),
            "name": getattr(message, 'name', None),
            "tool_calls": getattr(message, 'tool_calls', None),
            "tool_call_id": getattr(message, 'tool_call_id', None),
        }
        
        # Filtrar valores None para limpiar el output
        return {k: v for k, v in message_data.items() if v is not None}
    
    def _serialize_value(self, value) -> Any:
        """
        Serializar un valor usando métodos inteligentes.
        
        Detecta automáticamente el tipo y usa el método de serialización apropiado.
        """
        try:
            # Intentar serialización directa primero
            json.dumps(value)
            return value
            
        except (TypeError, ValueError):
            # Si no es serializable, usar métodos específicos
            
            # Para objetos Pydantic
            if hasattr(value, 'model_dump'):
                return value.model_dump()
            elif hasattr(value, 'dict'):
                return value.dict()
            
            # Para objetos con to_dict
            elif hasattr(value, 'to_dict'):
                return value.to_dict()
            
            # Para objetos con __dict__
            elif hasattr(value, '__dict__'):
                return {k: self._serialize_value(v) for k, v in value.__dict__.items()}
            
            # Para listas y tuplas
            elif isinstance(value, (list, tuple)):
                return [self._serialize_value(item) for item in value]
            
            # Para diccionarios
            elif isinstance(value, dict):
                return {k: self._serialize_value(v) for k, v in value.items()}
            
            # Fallback final: convertir a string
            else:
                return str(value)


class LogManager:
    """Manager centralizado para logging del grafo"""
    
    def __init__(self):
        self.observers: List[LogObserver] = []
        self.enabled = True
        self.log_level = LogLevel.INFO
    
    def add_observer(self, observer: LogObserver):
        """Agregar un observador de logging"""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: LogObserver):
        """Remover un observador de logging"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def log_state_change(self, agent_name: str, event_type: str, state: Dict[str, Any], 
                        processing_time: Optional[float] = None,
                        prompt: Optional[str] = None, response: Optional[str] = None):
        """Log un cambio de estado"""
        if not self.enabled:
            return
        
        event = StateChangeEvent(
            agent_name=agent_name,
            event_type=event_type,
            state=state,
            timestamp=datetime.now(),
            processing_time=processing_time,
            prompt=prompt,
            response=response
        )
        
        # Notificar a todos los observadores
        for observer in self.observers:
            try:
                observer.on_state_change(event)
            except Exception as e:
                print(f"❌ Error en observador de logging: {e}")
    
    def log_before_agent(self, agent_name: str, state: Dict[str, Any], prompt: Optional[str] = None):
        """Log antes de ejecutar un agente"""
        self.log_state_change(agent_name, "BEFORE", state, prompt=prompt)
    
    def log_after_agent(self, agent_name: str, state: Dict[str, Any], processing_time: float, response: Optional[str] = None):
        """Log después de ejecutar un agente"""
        self.log_state_change(agent_name, "AFTER", state, processing_time, response=response)
    
    def log_error(self, agent_name: str, error: Exception, state: Dict[str, Any]):
        """Log de errores en agentes"""
        error_state = {
            **state,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "timestamp": datetime.now().isoformat()
            }
        }
        self.log_state_change(agent_name, "ERROR", error_state)
    
    def set_log_level(self, level: LogLevel):
        """Cambiar el nivel de logging"""
        self.log_level = level
    
    def enable(self):
        """Habilitar logging"""
        self.enabled = True
    
    def disable(self):
        """Deshabilitar logging"""
        self.enabled = False
    
    def clear_observers(self):
        """Limpiar todos los observadores"""
        self.observers.clear()


# Instancia global del LogManager (Singleton)
_log_manager = None

def get_log_manager() -> LogManager:
    """Obtener la instancia global del LogManager"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
        # Agregar observadores por defecto
        _log_manager.add_observer(ConsoleLogObserver())
        _log_manager.add_observer(FileLogObserver())
    return _log_manager
