"""
Agente ValidateMessage para el grafo LangGraph.

Este agente valida si el mensaje del usuario está dentro del tópico de la conversación.
Usa un modelo LLM (OpenAI) para determinar si el mensaje es relevante al contexto
de finanzas personales y planificación financiera.
"""

import os
import json
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage
from .base_agent import BaseAgent
from prompts.validate_message_prompts import OFF_TOPIC_MESSAGE, VALIDATE_MESSAGE_SYSTEM_PROMPT

class ValidateMessageAgent(BaseAgent):
    """Agente que valida si el mensaje está dentro del tópico usando LLM"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implementar patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(ValidateMessageAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializar el agente validate message solo una vez"""
        if not self._initialized:
            # Configurar el modelo OpenAI para validación
            from langchain_openai import ChatOpenAI
            try:
                from config import Config
            except Exception:
                Config = None  # Fallback si no existe

            # Leer configuración desde Config si existe, si no desde variables de entorno
            api_key = (
                getattr(Config, "OPENAI_API_KEY", None) if Config else None
            ) or os.getenv("OPENAI_API_KEY", "")
            model_name = (
                getattr(Config, "OPENAI_MODEL", None) if Config else None
            ) or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            # Crear modelo específico para validación con parámetros optimizados
            self.model = ChatOpenAI(
                api_key=api_key,
                model=model_name,
                temperature=0.0,  # Determinístico para clasificación
                max_tokens=50,    # Solo necesitamos el JSON
            )

            # Llamar al constructor padre con el modelo configurado
            super().__init__(self.model, "validate_message")
            
            # Marcar como inicializado
            self._initialized = True

    def _process_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación del método abstracto requerido por BaseAgent"""
        print("---Validate Message Node---")
        
        # Crear el mensaje del sistema con las instrucciones
        system_message = SystemMessage(content=VALIDATE_MESSAGE_SYSTEM_PROMPT)
        
        # Preparar mensajes para el modelo (sistema + historial de mensajes)
        messages = [system_message] + state["messages"]
        
        # Preparar el prompt completo para logging
        prompt_text = self._prepare_prompt_text(messages)
        
        # Log del prompt completo
        self._log_prompt(state, prompt_text)
        
        try:
            # Llamar al modelo para obtener la clasificación
            response = self.model.invoke(messages)
            
            # Extraer el contenido de la respuesta
            from .agent_utils import extract_text_from_content
            response_text = extract_text_from_content(getattr(response, "content", response))
            
            print(f"[ValidateMessage] Respuesta del LLM: {response_text}")
            
            # Intentar parsear el JSON
            try:
                # Limpiar la respuesta por si tiene texto adicional
                response_text = response_text.strip()
                # Buscar el JSON en la respuesta
                if "{" in response_text and "}" in response_text:
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                    result_json = json.loads(json_str)
                    on_topic = result_json.get("onTopic", True)
                else:
                    # Si no hay JSON, asumir que está on-topic
                    print(f"[ValidateMessage] No se encontró JSON en la respuesta, asumiendo on-topic")
                    on_topic = True
            except json.JSONDecodeError as e:
                print(f"[ValidateMessage] Error parseando JSON: {e}, asumiendo on-topic")
                on_topic = True
            
            print(f"[ValidateMessage] onTopic: {on_topic}")
            
            # Preparar el resultado
            result = {
                "onTopic": on_topic,
                "last_agent": "validate_message"
            }
            
            # Si el mensaje está fuera de tópico, agregar el mensaje de respuesta
            if not on_topic:
                off_topic_message = AIMessage(content=OFF_TOPIC_MESSAGE)
                result["messages"] = [off_topic_message]
                print(f"[ValidateMessage] Mensaje fuera de tópico, agregando respuesta")
            else:
                print(f"[ValidateMessage] Mensaje válido, continuando flujo normal")
            
            return result
            
        except Exception as e:
            print(f"[ValidateMessage] Error en validación: {e}, asumiendo on-topic")
            # En caso de error, asumir que está on-topic para no interrumpir el flujo
            return {
                "onTopic": True,
                "last_agent": "validate_message"
            }

