import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from config import Config
from prompts.greeting_prompts import GREETING_BY_TYPE
from typing import Dict, Any, Optional, Literal
from log_manager import get_log_manager
from datetime import datetime

# Importar desde archivos separados
from state_manager import StateManager, ConversationStatus
from agents import ProfesorAgent, SummarizerAgent, ValidateReasonAgent, EvaluateCloseAgent, EndConversationAgent

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
    from prompts.greeting_prompts import GREETING_BY_TYPE
    
    # Resolver pregunta actual y crear mensaje de bienvenida dinámico
    current_question = state.get("question") or "¿Qué te gustaría resolver hoy?"
    # Seleccionar saludo directamente por enum value de pregunta
    mapping = GREETING_BY_TYPE.get(current_question)
    # Determinar texto de bienvenida
    if isinstance(mapping, dict):
        welcome_text = mapping.get("greeting", GREETING_MESSAGE)
    elif isinstance(mapping, str):
        welcome_text = mapping
    else:
        welcome_text = GREETING_MESSAGE
    welcome_message = AIMessage(content=welcome_text)
    
    # Retornar el mensaje de bienvenida y marcar como saludado
    # También actualizar el status y establecer la pregunta actual
    return {
        "messages": [welcome_message], 
        "greeted": True,
        "status": "exploring",  # Cambiar de "greeting" a "exploring"
        # Conservar el enum en estado; la UI/agents pueden resolver el texto por mapping
        "question": state.get("question", current_question),
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

# Importar ValidateReasonAgent para usar su lógica
from agents import ValidateReasonAgent

# Instancia global del ValidateReasonAgent
validate_reason_agent = ValidateReasonAgent()

# Instancia global del EvaluateCloseAgent
evaluate_close_agent = EvaluateCloseAgent()

# Instancia global del EndConversationAgent
end_conversation_agent = EndConversationAgent()

# Define the logic for the validate reason node
def validate_reason_node(state: State) -> State:
    """Nodo que valida si el usuario dio una razón válida"""
    print("---Validate Reason Node---")
    # Procesar el estado usando el ValidateReasonAgent y retornar el estado modificado
    return validate_reason_agent._process_state(state)

# Define the logic for the evaluate close node
def evaluate_close_node(state: State) -> State:
    """Nodo que evalúa si la conversación está lista para cerrar"""
    print("---Evaluate Close Node---")
    # Procesar el estado usando el EvaluateCloseAgent y retornar el estado modificado
    return evaluate_close_agent._process_state(state)

# Define the logic for the end conversation node
def end_conversation_node(state: State) -> State:
    """Nodo que finaliza la conversación"""
    print("---End Conversation Node---")
    # Procesar el estado usando el EndConversationAgent y retornar el estado modificado
    return end_conversation_agent._process_state(state)

# Define the logic for the conversation closed node
def conversation_closed_node(state: State) -> State:
    """Nodo que responde cuando la conversación ya fue cerrada"""
    print("---Conversation Closed Node---")
    
    # Crear mensaje informativo
    closed_message = AIMessage(content="La conversación ya ha sido cerrada. No se pueden procesar más mensajes.")
    
    # Agregar el mensaje al estado
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(closed_message)
    
    # Marcar el último agente
    state["last_agent"] = "conversation_closed"
    
    return state

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
    """Función que decide el siguiente nodo basado en el estado"""
    
    # Si la conversación ya fue cerrada, ir al nodo conversation_closed
    if state.get("status") == "end_conversation":
        print("Router seleccionó: conversation_closed (conversación ya cerrada)")
        return "conversation_closed"
    
    # Si no se ha saludado al usuario, ir al nodo de saludo
    if not state.get("greeted", False):
        print("Router seleccionó: greet (primera vez)")
        return "greet"
    
    # Si ya se saludó, ir al validate_reason para validar la respuesta del usuario
    print("Router seleccionó: validate_reason (ya saludado, validar respuesta)")
    return "validate_reason"

# Define the logic to route after the validate_reason has processed the state
def route_after_validation(state: State) -> str:
    """Función que decide el siguiente nodo después de que validate_reason procesó el estado"""
    status = state.get("status")
    
    if status == "asking_confirmation":
        print("ValidateReason seleccionó: confirmation (usuario dio razón válida, pedir confirmación)")
        return "confirmation"
    elif status == "waiting_confirmation":
        print("ValidateReason seleccionó: evaluate_close (usuario ya está en confirmación, evaluar si cerrar)")
        return "evaluate_close"
    elif status == "exploring":
        print("ValidateReason seleccionó: profesor (usuario no dio razón válida, continuar explorando)")
        return "profesor"
    else:
        print(f"ValidateReason seleccionó: profesor (status desconocido: {status})")
        return "profesor"

# Define the logic to route after the evaluate_close has processed the state
def route_after_evaluate_close(state: State) -> str:
    """Función que decide el siguiente nodo después de que evaluate_close procesó el estado"""
    status = state.get("status")
    
    if status == "confirmed":
        print("EvaluateClose seleccionó: end_conversation (usuario confirmó, finalizar conversación)")
        return "end_conversation"
    elif status == "waiting_confirmation":
        print("EvaluateClose seleccionó: confirmation (usuario sigue esperando confirmación)")
        return "confirmation"
    elif status == "exploring":
        print("EvaluateClose seleccionó: profesor (usuario no dio razón válida, continuar explorando)")
        return "profesor"
    else:
        print(f"EvaluateClose seleccionó: profesor (status desconocido: {status})")
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
        workflow.add_node("validate_reason", validate_reason_node)  # Nodo validate reason que valida el estado
        workflow.add_node("evaluate_close", evaluate_close_node)  # Nodo que evalúa si cerrar
        workflow.add_node("confirmation", call_confirmation_agent)  # Nodo confirmador
        workflow.add_node("end_conversation", end_conversation_node)  # Nodo que finaliza la conversación
        workflow.add_node("conversation_closed", conversation_closed_node)  # Nodo para conversación cerrada
        workflow.add_node("profesor", call_profesor_agent)
        workflow.add_node("summarize_conversation", summarize_conversation)
        
        # Set the entrypoint with routing
        workflow.add_conditional_edges(
            START,
            route_to_agent,
            {
                "greet": "greet",
                "validate_reason": "validate_reason",
                "conversation_closed": "conversation_closed"
            }
        )
        
        # Add conditional edges to decide whether to continue or summarize
        # El nodo greet siempre termina (solo saluda)
        workflow.add_edge("greet", END)
        
        # El nodo conversation_closed siempre termina (conversación ya cerrada)
        workflow.add_edge("conversation_closed", END)
        
        # El validate_reason va a la decisión de ruta
        workflow.add_conditional_edges(
            "validate_reason",
            route_after_validation,
            {
                "confirmation": "confirmation",
                "evaluate_close": "evaluate_close",
                "profesor": "profesor"
            }
        )
        
        # El evaluate_close va a la decisión de ruta (manteniendo la lógica original)
        workflow.add_conditional_edges(
            "evaluate_close",
            route_after_evaluate_close,
            {
                "confirmation": "confirmation",
                "end_conversation": "end_conversation",
                "profesor": "profesor"
            }
        )
        
        # El nodo confirmador va a should_continue para decidir si resumir o terminar
        workflow.add_conditional_edges(
            "confirmation",
            should_continue,
            {
                "summarize_conversation": "summarize_conversation",
                "__end__": END
            }
        )
        
        # El nodo end_conversation va a should_continue para decidir si resumir o terminar
        workflow.add_conditional_edges(
            "end_conversation",
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
    
    def process_message(self, message: str, session_id: str, user: Optional[str] = None, question: str = "", tipo_objetivo: Optional[str] = None) -> Dict[str, Any]:
        """Procesar un mensaje a través del grafo
        
        Args:
            message: El mensaje del usuario
            session_id: ID de la sesión
            user: Usuario opcional
            question: Tipo de pregunta actual
            tipo_objetivo: Si la pregunta es objetivo, especifica el tipo elegido previamente
        """
        user_message = HumanMessage(content=message)
        
        # Ajustar el tipo de pregunta basado en tipo_objetivo si es necesario
        if question == "objetivo" and tipo_objetivo:
            if tipo_objetivo == "Monto final":
                question = "objetivo_monto_final"
            elif tipo_objetivo == "Renta":
                question = "objetivo_renta"
            elif tipo_objetivo == "Duración":
                question = "objetivo_duracion"
            print(f"[GraphInterface] Ajustando pregunta objetivo según tipo: {question}")
        
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
                    
                    # Actualizar la pregunta con el nuevo tipo
                    initial_state["question"] = question
                        
                else:
                    # Si no hay mensajes, crear estado nuevo
                    initial_state = self.state_manager.create_initial_state(user_message, user)
                    # Setear pregunta
                    initial_state["question"] = question
            else:
                # Si no hay estado existente, crear uno nuevo
                initial_state = self.state_manager.create_initial_state(user_message, user)
                # Setear pregunta
                initial_state["question"] = question
                
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
