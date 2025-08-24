import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from config import Config
from typing import Dict, Any, Optional, Literal
from log_manager import get_log_manager
from datetime import datetime

# Importar desde archivos separados
from state_manager import StateManager, ConversationStatus
from agents import NiñoAgent, AncianoAgent, ProfesorAgent, SummarizerAgent, RouterAgent

# We will use this model for both the conversation and the summarization
model = ChatGroq(
    api_key=Config.GROQ_API_KEY,
    model=Config.GROQ_MODEL,
    temperature=Config.GROQ_TEMPERATURE
)



# State class to store messages and summary
class State(MessagesState):
    summary: str
    status: ConversationStatus
    greeted: bool
    reason: Optional[str]
    question: Optional[str]
    created_at: datetime
    updated_at: datetime
    user: Optional[str]
    last_agent: Optional[str]  # Agregar campo para trackear el último agente

# Define the logic to call the niño agent
def call_niño_agent(state: State):
    """Nodo que responde como un niño"""
    print("---Niño Node---")
    
    # Importar la configuración del agente niño
    from prompts import NIÑO_AGENT_CONFIG, NIÑO_WITH_SUMMARY_PROMPT
    
    # Get summary if it exists
    summary = state.get("summary", "")
    
    # Create system message with summary context if available
    if summary:
        system_content = NIÑO_WITH_SUMMARY_PROMPT.format(
            base_prompt=NIÑO_AGENT_CONFIG['base_prompt'],
            summary=summary
        )
    else:
        system_content = NIÑO_AGENT_CONFIG['base_prompt']
    
    system_message = SystemMessage(content=system_content)
    
    # Prepare messages for the model
    messages = [system_message] + state["messages"]
    
    response = model.invoke(messages)
    return {"messages": [response], "last_agent": "niño"}

# Define the logic to call the anciano agent
def call_anciano_agent(state: State):
    """Nodo que responde como un anciano"""
    print("---Anciano Node---")
    
    # Importar la configuración del agente anciano
    from prompts import ANCIANO_AGENT_CONFIG, ANCIANO_WITH_SUMMARY_PROMPT
    
    # Get summary if it exists
    summary = state.get("summary", "")
    
    # Create system message with summary context if available
    if summary:
        system_content = ANCIANO_WITH_SUMMARY_PROMPT.format(
            base_prompt=ANCIANO_AGENT_CONFIG['base_prompt'],
            summary=summary
        )
    else:
        system_content = ANCIANO_AGENT_CONFIG['base_prompt']
    
    system_message = SystemMessage(content=system_content)
    
    # Prepare messages for the model
    messages = [system_message] + state["messages"]
    
    response = model.invoke(messages)
    return {"messages": [response], "last_agent": "anciano"}

# Define the logic to call the profesor agent
def call_profesor_agent(state: State):
    """Nodo que responde como un profesor"""
    print("---Profesor Node---")
    
    # Importar y usar la clase ProfesorAgent optimizada
    from agents import ProfesorAgent
    
    # Crear instancia del agente y procesar el estado
    profesor_agent = ProfesorAgent()
    result = profesor_agent.invoke(state)  # ← Usar invoke() en lugar de process_state()
    
    # Asegurar que se incluya last_agent en el resultado
    if "last_agent" not in result:
        result["last_agent"] = "profesor"
    
    return result

# Define the logic to greet the user
def call_greet_agent(state: State):
    """Nodo que saluda al usuario por primera vez"""
    print("---Greet Node---")
    
    # Importar el mensaje de bienvenida desde prompts
    from prompts import GREETING_MESSAGE
    
    # Crear mensaje de bienvenida
    welcome_message = AIMessage(content=GREETING_MESSAGE)
    
    # Retornar el mensaje de bienvenida y marcar como saludado
    # También actualizar el status y establecer la pregunta actual
    return {
        "messages": [welcome_message], 
        "greeted": True,
        "status": "exploring",  # Cambiar de "greeting" a "exploring"
        "question": "¿Qué tipo de plan te gustaría elegir? Puedes decirme si prefieres Monto final, Renta, Duración, o si tienes dudas sobre alguno.",
        "last_agent": "greet"  # Marcar que el agente de saludo respondió
    }

# Define the logic to summarize the conversation
def summarize_conversation(state: State):
    """Nodo que resume la conversación"""
    print("---Resumen de Conversación---")
    
    # Importar los prompts de resumen
    from prompts import SUMMARY_EXTEND_PROMPT, SUMMARY_CREATE_PROMPT, SUMMARY_EXTEND_WITH_CONTEXT
    
    # Obtener el resumen existente si existe
    summary = state.get("summary", "")
    
    # Crear el prompt de resumen
    if summary:
        summary_message = SUMMARY_EXTEND_WITH_CONTEXT.format(
            summary=summary,
            extend_prompt=SUMMARY_EXTEND_PROMPT
        )
    else:
        summary_message = SUMMARY_CREATE_PROMPT
    
    # Agregar el prompt a nuestro historial
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    
    response = model.invoke(messages)
    
    # Eliminar todos los mensajes excepto los 2 más recientes y agregar el resumen al estado
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    
    return {
        "summary": response.content, 
        "messages": delete_messages
    }

# Importar RouterAgent para usar su lógica
from agents import RouterAgent

# Instancia global del RouterAgent
router_agent = RouterAgent()

# Define the logic for the router node
def router_node(state: State) -> State:
    """Nodo que analiza la respuesta del usuario y actualiza el estado"""
    print("---Router Node---")
    # Procesar el estado usando el RouterAgent y retornar el estado modificado
    return router_agent._process_state(state)

# Define the logic for the confirmation agent
def call_confirmation_agent(state: State) -> State:
    """Nodo que pide confirmación de la razón del usuario"""
    from agents import ConfirmationAgent
    confirmation_agent = ConfirmationAgent()
    result = confirmation_agent.invoke(state)
    
    # Asegurar que se incluya last_agent en el resultado
    if "last_agent" not in result:
        result["last_agent"] = "confirmation"
    
    return result

# Define the logic to route to the appropriate agent
def route_to_agent(state: State) -> str:
    """Función que decide el siguiente nodo basado en el estado procesado por el router"""
    
    # Si no se ha saludado al usuario, ir al nodo de saludo
    if not state.get("greeted", False):
        print("Router seleccionó: greet (primera vez)")
        return "greet"
    
    # Si ya se saludó, ir al router para procesar la respuesta del usuario
    print("Router seleccionó: router (ya saludado, procesar respuesta)")
    return "router"

# Define the logic to route after the router has processed the state
def route_after_router(state: State) -> str:
    """Función que decide el siguiente nodo después de que el router procesó el estado"""
    status = state.get("status")
    
    if status == "waiting_confirmation":
        print("Router seleccionó: confirmation (usuario dio razón válida, pedir confirmación)")
        return "confirmation"
    elif status == "exploring":
        print("Router seleccionó: profesor (usuario no dio razón válida, continuar explorando)")
        return "profesor"
    else:
        print(f"Router seleccionó: profesor (status desconocido: {status})")
        return "profesor"

# Determine whether to end or summarize the conversation
def should_continue(state: State) -> Literal["summarize_conversation", "__end__"]:
    """Determina si continuar la conversación o resumir
    
    SIGUE EL PATRÓN DEL EJEMPLO ORIGINAL:
    - Si hay más de 6 mensajes: resumir y terminar
    - Si hay 6 o menos mensajes: terminar directamente
    """
    messages = state["messages"]
    
    # Si hay más de 6 mensajes, resumir la conversación
    if len(messages) > 6:
        return "summarize_conversation"
    
    # De lo contrario, terminar
    return "__end__"

# Eliminar la función after_summary_route ya que no se necesita

class GraphInterface:
    """Interfaz para manejar la lógica de LangGraph - Patrón Singleton"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphInterface, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el grafo solo una vez"""
        if not self._initialized:
            self.log_manager = get_log_manager()
            self.state_manager = StateManager()
            # Crear el grafo
            self.graph = self._create_graph()
            self._initialized = True
    
    def _create_graph(self):
        """Crear y compilar el grafo"""
        conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        memory = SqliteSaver(conn)
        
        # Define a new graph
        workflow = StateGraph(State)
        
        # Add nodes using the pure functions
        workflow.add_node("greet", call_greet_agent)
        workflow.add_node("router", router_node)  # Nodo router que procesa el estado
        workflow.add_node("confirmation", call_confirmation_agent)  # Nodo confirmador
        workflow.add_node("niño", call_niño_agent)
        workflow.add_node("anciano", call_anciano_agent)
        workflow.add_node("profesor", call_profesor_agent)
        workflow.add_node("summarize_conversation", summarize_conversation)
        
        # Set the entrypoint with routing
        workflow.add_conditional_edges(
            START,
            route_to_agent,
            {
                "greet": "greet",
                "router": "router"
            }
        )
        
        # Add conditional edges to decide whether to continue or summarize
        # El nodo greet siempre termina (solo saluda)
        workflow.add_edge("greet", END)
        
        # El router va a la decisión de ruta
        workflow.add_conditional_edges(
            "router",
            route_after_router,
            {
                "confirmation": "confirmation",
                "profesor": "profesor",
                "niño": "niño",
                "anciano": "anciano"
            }
        )
        
        # El nodo confirmador termina para esperar la respuesta del usuario
        workflow.add_edge("confirmation", END)
        
        workflow.add_conditional_edges(
            "niño",
            should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        workflow.add_conditional_edges(
            "anciano",
            should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        workflow.add_conditional_edges(
            "profesor",
            should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        # The summarize node always ends (like in the original example)
        workflow.add_edge("summarize_conversation", END)
        
        # Compile
        return workflow.compile(checkpointer=memory)
    
    def process_message(self, message: str, session_id: str, user: Optional[str] = None) -> Dict[str, Any]:
        """Procesar un mensaje a través del grafo"""
        user_message = HumanMessage(content=message)
        
        # Intentar recuperar el estado existente del checkpoint
        try:
            # Obtener el estado actual del checkpoint
            current_state = self.graph.get_state({"configurable": {"thread_id": session_id}})
            
            # Si hay estado existente, agregar solo el nuevo mensaje
            if current_state and hasattr(current_state, 'values') and current_state.values:
                # Convertir StateSnapshot a dict y preservar todos los campos
                current_dict = dict(current_state.values)
                
                if current_dict.get("messages"):
                    # Preservar todos los campos del estado existente
                    initial_state = dict(current_dict)
                    # Agregar el nuevo mensaje del usuario
                    initial_state["messages"] = current_dict["messages"] + [user_message]
                    # Actualizar timestamp
                    initial_state["updated_at"] = datetime.now()
                    
                    # Si es el primer mensaje de la sesión, establecer el usuario
                    if not initial_state.get("user") and user:
                        initial_state["user"] = user
                        
                else:
                    # Si no hay mensajes, crear estado nuevo
                    initial_state = self.state_manager.create_initial_state(user_message, user)
            else:
                # Si no hay estado existente, crear uno nuevo
                initial_state = self.state_manager.create_initial_state(user_message, user)
                
        except Exception as e:
            # Si hay algún error al recuperar el estado, crear uno nuevo
            print(f"⚠️ Error recuperando estado del checkpoint: {e}")
            initial_state = self.state_manager.create_initial_state(user_message, user)
        
        # Procesar el mensaje a través del grafo
        result = self.graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}}
        )
        
        return result
    

    
    # Métodos de conveniencia que delegan al StateManager
    def update_status(self, state: State, new_status: ConversationStatus) -> State:
        """Actualizar el status de la conversación"""
        return self.state_manager.update_status(state, new_status)
    
    def set_greeted(self, state: State, greeted: bool = True) -> State:
        """Marcar que se ha saludado al usuario"""
        return self.state_manager.set_greeted(state, greeted)
    
    def set_reason(self, state: State, reason: str) -> State:
        """Establecer la razón de la conversación"""
        return self.state_manager.set_reason(state, reason)
    
    def set_question(self, state: State, question: str) -> State:
        """Establecer la pregunta actual"""
        return self.state_manager.set_question(state, question)
    
    def get_state_info(self, state: State) -> Dict[str, Any]:
        """Obtener información resumida del estado"""
        return self.state_manager.get_state_info(state)
