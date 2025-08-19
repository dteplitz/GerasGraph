import random
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from config import Config
from typing import Dict, Any, Literal
from log_manager import get_log_manager

# State class to store messages and summary
class State(MessagesState):
    summary: str

class GraphInterface:
    """Interfaz para manejar la lógica de LangGraph - Patrón Singleton"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphInterface, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el modelo Groq y crear el grafo solo una vez"""
        if not self._initialized:
            self.model = ChatGroq(
                model=Config.GROQ_MODEL,
                temperature=Config.GROQ_TEMPERATURE
            )
            self.graph = self._create_graph()
            self.log_manager = get_log_manager()
            self._initialized = True
    
    def _niño_node(self, state: State) -> Dict[str, Any]:
        """Nodo que responde como un niño"""
        start_time = time.time()
        
        try:
            print("---Niño Node---")
            
            # Get summary if it exists
            summary = state.get("summary", "")
            
            # Create system message with summary context if available
            if summary:
                system_content = f"Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño.\n\nResumen de la conversación anterior: {summary}"
            else:
                system_content = "Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño."
            
            system_message = SystemMessage(content=system_content)
            
            # Preparar el prompt completo para logging
            prompt_messages = [system_message] + state["messages"]
            prompt_text = "\n".join([f"{msg.type}: {msg.content}" for msg in prompt_messages])
            
            # Log estado antes del agente con el prompt completo
            self.log_manager.log_before_agent("niño", state, prompt_text)
            
            response = self.model.invoke(prompt_messages)
            result = {"messages": [response]}
            
            # Log estado después del agente con prompt y respuesta
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent("niño", result, processing_time, response.content)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error("niño", e, state)
            raise
    
    def _anciano_node(self, state: State) -> Dict[str, Any]:
        """Nodo que responde como un anciano"""
        start_time = time.time()
        
        try:
            print("---Anciano Node---")
            
            # Get summary if it exists
            summary = state.get("summary", "")
            
            # Create system message with summary context if available
            if summary:
                system_content = f"Eres un anciano sabio de 80 años. Responde con experiencia, paciencia y sabiduría. Usa un tono reflexivo y comparte lecciones de vida cuando sea apropiado.\n\nResumen de la conversación anterior: {summary}"
            else:
                system_content = "Eres un anciano sabio de 80 años. Responde con experiencia, paciencia y sabiduría. Usa un tono reflexivo y comparte lecciones de vida cuando sea apropiado."
            
            system_message = SystemMessage(content=system_content)
            
            # Preparar el prompt completo para logging
            prompt_messages = [system_message] + state["messages"]
            prompt_text = "\n".join([f"{msg.type}: {msg.content}" for msg in prompt_messages])
            
            # Log estado antes del agente con el prompt completo
            self.log_manager.log_before_agent("anciano", state, prompt_text)
            
            response = self.model.invoke(prompt_messages)
            result = {"messages": [response]}
            
            # Log estado después del agente con prompt y respuesta
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent("anciano", result, processing_time, response.content)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error("anciano", e, state)
            raise
    
    def _route_to_random(self, state: State) -> str:
        """Función que decide aleatoriamente el siguiente nodo"""
        agents = ["niño", "anciano"]
        selected = random.choice(agents)
        
        print(f"Router seleccionó: {selected}")
        return selected
    
    def _should_continue(self, state: State) -> Literal["summarize_conversation", "__end__"]:
        """Determina si continuar la conversación o resumir"""
        messages = state["messages"]
        
        # Si hay más de 6 mensajes, resumir la conversación
        if len(messages) > 6:
            return "summarize_conversation"
        
        # De lo contrario, terminar
        return END
    
    def _summarize_conversation(self, state: State) -> Dict[str, Any]:
        """Nodo que resume la conversación"""
        start_time = time.time()
        
        try:
            print("---Resumen de Conversación---")
            
            # Obtener el resumen existente si existe
            summary = state.get("summary", "")
            
            # Crear el prompt de resumen
            if summary:
                summary_message = (
                    f"Este es el resumen de la conversación hasta ahora: {summary}\n\n"
                    "Extiende el resumen teniendo en cuenta los nuevos mensajes arriba:"
                )
            else:
                summary_message = "Crea un resumen de la conversación arriba:"
            
            # Agregar el prompt a nuestro historial
            messages = state["messages"] + [HumanMessage(content=summary_message)]
            
            # Preparar el prompt completo para logging
            prompt_text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
            
            # Log estado antes del agente con el prompt completo
            self.log_manager.log_before_agent("summarize_conversation", state, prompt_text)
            
            response = self.model.invoke(messages)
            
            # Eliminar todos los mensajes excepto los 2 más recientes y agregar el resumen al estado
            delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
            
            result = {"summary": response.content, "messages": delete_messages}
            
            # Log estado después del agente con prompt y respuesta
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent("summarize_conversation", result, processing_time, response.content)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error("summarize_conversation", e, state)
            raise
    
    def _create_graph(self):
        """Crear y compilar el grafo"""
        conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        memory = SqliteSaver(conn)
        
        workflow = StateGraph(State)
        
        # Agregar nodos
        workflow.add_node("niño", self._niño_node)
        workflow.add_node("anciano", self._anciano_node)
        workflow.add_node("summarize_conversation", self._summarize_conversation)
        
        # Agregar edges con routing condicional
        workflow.add_conditional_edges(
            START,
            self._route_to_random,
            {
                "niño": "niño",
                "anciano": "anciano"
            }
        )
        
        # Agregar edges condicionales para decidir si continuar o resumir
        workflow.add_conditional_edges(
            "niño",
            self._should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        workflow.add_conditional_edges(
            "anciano",
            self._should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        # El nodo de resumen siempre termina
        workflow.add_edge("summarize_conversation", END)
        
        return workflow.compile(checkpointer=memory)
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Procesar un mensaje a través del grafo"""
        user_message = HumanMessage(content=message)
        
        result = self.graph.invoke(
            {"messages": [user_message], "summary": ""},
            config={"configurable": {"thread_id": session_id}}
        )
        
        return result
    
    def get_agent_type(self, response_text: str) -> str:
        """Determinar el tipo de agente basado en la respuesta"""
        niño_keywords = ["niño", "niña", "pequeño", "juego", "diversión", "¡", "wow", "genial"]
        
        if any(word in response_text.lower() for word in niño_keywords):
            return "niño"
        else:
            return "anciano"
