"""
Agente Router para el grafo LangGraph.

Este agente se encarga de decidir el flujo de la conversación y cuándo resumir.
"""

import random
from typing import Dict, Any, Literal
from langgraph.graph import END

class RouterAgent:
    """Agente que decide el flujo de la conversación"""
    
    def __init__(self):
        """Inicializar el agente router"""
        pass
    
    def route_to_random_agent(self, state: Dict[str, Any]) -> str:
        """Función que decide aleatoriamente el siguiente nodo"""
        agents = ["niño", "anciano"]
        selected = random.choice(agents)
        
        print(f"Router seleccionó: {selected}")
        return selected
    
    def should_continue(self, state: Dict[str, Any]) -> Literal["summarize_conversation", "__end__"]:
        """Determina si continuar la conversación o resumir"""
        messages = state["messages"]
        
        # Si hay más de 6 mensajes, resumir la conversación
        if len(messages) > 6:
            return "summarize_conversation"
        
        # De lo contrario, terminar
        return END
