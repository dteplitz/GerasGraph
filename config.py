"""
Configuración centralizada para la aplicación GerasGraph.
Lee las variables de entorno y proporciona valores por defecto.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Clase de configuración que lee variables de entorno"""
    
    # API Key de Groq (obligatorio)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Modelo de Groq a usar (opcional)
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    
    # Temperatura del modelo (opcional)
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.1"))
    
    # Ruta de la base de datos SQLite (opcional)
    DB_PATH: str = os.getenv("DB_PATH", "agent_memory.db")
    
    # ID de la sesión (opcional)
    SESSION_ID: str = os.getenv("SESSION_ID", "user_session_1")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración sea correcta"""
        if not cls.GROQ_API_KEY:
            print("ERROR: GROQ_API_KEY no está configurada.")
            print("Por favor, crea un archivo .env con tu API key de Groq:")
            print("GROQ_API_KEY=tu_api_key_aqui")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        """Imprime la configuración actual (sin mostrar la API key)"""
        print("Configuración actual:")
        print(f"  Modelo: {cls.GROQ_MODEL}")
        print(f"  Temperatura: {cls.GROQ_TEMPERATURE}")
        print(f"  Base de datos: {cls.DB_PATH}")
        print(f"  Sesión: {cls.SESSION_ID}")
        print(f"  API Key configurada: {'Sí' if cls.GROQ_API_KEY else 'No'}")

