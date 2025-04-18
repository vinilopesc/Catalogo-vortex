"""
Módulo de configuração de conexão com o banco de dados MySQL.
Otimizado para alta performance e consistência entre ambientes.
"""

import mysql.connector
import os
import logging
from dotenv import load_dotenv

# Configurar logger
logger = logging.getLogger(__name__)

# Carregar variáveis do arquivo .env
load_dotenv()

# Cache de conexão
connection_pool = None

def get_connection_pool():
    """
    Retorna o pool de conexões MySQL.
    Cria o pool se ele ainda não existir.
    """
    global connection_pool

    if connection_pool is None:
        try:
            from mysql.connector import pooling

            # Configurações do pool
            config = {
                'host': os.getenv("DB_HOST", "localhost"),
                'user': os.getenv("DB_USER", "root"),
                'password': os.getenv("DB_PASSWORD", ""),
                'database': os.getenv("DB_NAME", "catalogo_vortex"),
                'charset': 'utf8mb4',
                'use_unicode': True,
                'get_warnings': True,
                'autocommit': False,  # Controle de transações explícito
                'pool_name': 'vortex_pool',
                'pool_size': 5  # Tamanho inicial do pool
            }

            connection_pool = pooling.MySQLConnectionPool(**config)
            logger.info("Pool de conexões MySQL inicializado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao criar pool de conexões: {str(e)}")
            raise

    return connection_pool

def get_db_connection():
    """
    Retorna uma conexão ativa com o banco de dados MySQL.
    Versão otimizada com suporte a pooling.
    """
    try:
        # Tentar obter conexão do pool
        pool = get_connection_pool()
        conn = pool.get_connection()

        # Configurar para retornar dicionários nos resultados
        conn.cursor_class = mysql.connector.cursor.MySQLCursorDict

        return conn

    except Exception as e:
        logger.error(f"Erro ao obter conexão do pool: {str(e)}")

        # Fallback para conexão direta sem pool em caso de erro
        logger.warning("Tentando conexão direta como fallback")
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "catalogo_vortex"),
                charset='utf8mb4'
            )
            return conn
        except Exception as e2:
            logger.critical(f"Erro fatal ao conectar ao banco de dados: {str(e2)}")
            raise