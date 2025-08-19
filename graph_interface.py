import random
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from config import Config
from typing import Dict, Any
from log_manager import get_log_manager

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
    
    def _niño_node(self, state: MessagesState) -> Dict[str, Any]:
        """Nodo que responde como un niño"""
        start_time = time.time()
        
        # Log estado antes del agente
        self.log_manager.log_before_agent("niño", state)
        
        try:
            print("---Niño Node---")
            
            system_message = SystemMessage(
                content="Eres un niño de 8 años. Responde de manera infantil, con emoción y curiosidad. Usa lenguaje simple y expresiones típicas de un niño."
            )
            
            response = self.model.invoke([system_message] + state["messages"])
            result = {"messages": [response]}
            
            # Log estado después del agente
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent("niño", result, processing_time)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error("niño", e, state)
            raise
    
    def _anciano_node(self, state: MessagesState) -> Dict[str, Any]:
        """Nodo que responde como un anciano"""
        start_time = time.time()
        
        # Log estado antes del agente
        self.log_manager.log_before_agent("anciano", state)
        
        try:
            print("---Anciano Node---")
            
            system_message = SystemMessage(
                content="Eres un anciano sabio de 80 años. Responde con experiencia, paciencia y sabiduría. Usa un tono reflexivo y comparte lecciones de vida cuando sea apropiado."
            )
            
            response = self.model.invoke([system_message] + state["messages"])
            result = {"messages": [response]}
            
            # Log estado después del agente
            processing_time = time.time() - start_time
            self.log_manager.log_after_agent("anciano", result, processing_time)
            
            return result
            
        except Exception as e:
            # Log de error
            processing_time = time.time() - start_time
            self.log_manager.log_error("anciano", e, state)
            raise
    
    def _route_to_random(self, state: MessagesState) -> str:
        """Función que decide aleatoriamente el siguiente nodo"""
        agents = ["niño", "anciano"]
        selected = random.choice(agents)
        
        print(f"Router seleccionó: {selected}")
        return selected
    
    def _create_graph(self):
        """Crear y compilar el grafo"""
        conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        memory = SqliteSaver(conn)
        
        builder = StateGraph(MessagesState)
        
        # Agregar nodos
        builder.add_node("niño", self._niño_node)
        builder.add_node("anciano", self._anciano_node)
        
        # Agregar edges con routing condicional
        builder.add_conditional_edges(
            START,
            self._route_to_random,
            {
                "niño": "niño",
                "anciano": "anciano"
            }
        )
        builder.add_edge("niño", END)
        builder.add_edge("anciano", END)
        
        return builder.compile(checkpointer=memory)
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Procesar un mensaje a través del grafo"""
        user_message = HumanMessage(content=message)
        
        result = self.graph.invoke(
            {"messages": [user_message]},
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
