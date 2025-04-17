"""
Módulo de configuração de conexão com o banco de dados MySQL.
Simplificado para garantir melhor compatibilidade e estabilidade.
"""

import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Configurar logger
logger = logging.getLogger("db_connection")

# Carregar variáveis do arquivo .env
load_dotenv()

def get_db_connection():
    """
    Retorna uma conexão ativa com o banco de dados MySQL.
    Versão simplificada para maior compatibilidade.
    """
    try:
        # Usar configuração mínima para maior compatibilidade
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "dev_catalogo")
        )
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise