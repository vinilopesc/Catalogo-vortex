"""
Gerenciador de banco de dados para verificar e criar tabelas automaticamente.
Este módulo é executado durante a inicialização da aplicação para garantir
que todas as tabelas necessárias existam no banco de dados.
"""

import logging
import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
from backend.infrastructure.config_db import get_db_connection
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_manager")

# Carregar variáveis de ambiente
load_dotenv()

def get_app_db_connection():
    """
    Obtém uma conexão com o banco de dados da aplicação utilizando
    a função existente em config_db.py
    """
    return get_db_connection()

def table_exists(table_name):
    """
    Verifica se uma tabela específica existe no banco de dados.
    """
    conn = get_app_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone() is not None
        logger.info(f"Tabela '{table_name}' {'existe' if exists else 'não existe'}")
        return exists
    except Exception as e:
        logger.error(f"Erro ao verificar existência da tabela '{table_name}': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_usuarios_table():
    """
    Cria a tabela de usuários se ela não existir.
    """
    if table_exists('usuarios'):
        return True

    logger.info("Criando tabela 'usuarios'...")
    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                senha_hash VARCHAR(255) NOT NULL,
                senha_bruta VARCHAR(100),
                tipo ENUM('funcionario', 'gerente', 'dev') NOT NULL DEFAULT 'funcionario',
                data_criacao DATETIME NOT NULL,
                deletado BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
        logger.info("Tabela 'usuarios' criada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'usuarios': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_produtos_table():
    """
    Cria a tabela de produtos se ela não existir.
    """
    if table_exists('produtos'):
        return True

    logger.info("Criando tabela 'produtos'...")
    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco DECIMAL(10, 2) NOT NULL,
                quantidade_estoque INT NOT NULL DEFAULT 0,
                imagem_url VARCHAR(255),
                data_criacao DATETIME NOT NULL,
                deletado BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
        logger.info("Tabela 'produtos' criada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'produtos': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_pedidos_table():
    """
    Cria a tabela de pedidos se ela não existir.
    """
    if table_exists('pedidos'):
        return True

    logger.info("Criando tabela 'pedidos'...")
    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_nome VARCHAR(100) NOT NULL,
                cliente_telefone VARCHAR(20) NOT NULL,
                cliente_email VARCHAR(150),
                cliente_endereco TEXT NOT NULL,
                status ENUM('Pendente', 'Concluído') NOT NULL DEFAULT 'Pendente',
                data_pedido VARCHAR(20) NOT NULL,
                data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deletado BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
        logger.info("Tabela 'pedidos' criada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'pedidos': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_itens_pedido_table():
    """
    Cria a tabela de itens de pedido se ela não existir.
    Depende das tabelas 'pedidos' e 'produtos'.
    """
    if table_exists('itens_pedido'):
        return True

    # Verificar se as tabelas dependentes existem
    if not table_exists('pedidos') or not table_exists('produtos'):
        logger.error("Não é possível criar tabela 'itens_pedido': tabelas 'pedidos' ou 'produtos' não existem")
        return False

    logger.info("Criando tabela 'itens_pedido'...")
    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE itens_pedido (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pedido_id INT NOT NULL,
                produto_id INT NOT NULL,
                quantidade INT NOT NULL,
                preco_unitario DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)
        conn.commit()
        logger.info("Tabela 'itens_pedido' criada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'itens_pedido': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_tokens_recuperacao_table():
    """
    Cria a tabela de tokens de recuperação se ela não existir.
    Depende da tabela 'usuarios'.
    """
    if table_exists('tokens_recuperacao'):
        return True

    # Verificar se a tabela dependente existe
    if not table_exists('usuarios'):
        logger.error("Não é possível criar tabela 'tokens_recuperacao': tabela 'usuarios' não existe")
        return False

    logger.info("Criando tabela 'tokens_recuperacao'...")
    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE tokens_recuperacao (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                token VARCHAR(100) NOT NULL,
                validade FLOAT NOT NULL,
                usado BOOLEAN NOT NULL DEFAULT 0,
                data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        conn.commit()
        logger.info("Tabela 'tokens_recuperacao' criada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'tokens_recuperacao': {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_admin_user_if_not_exists():
    """
    Cria um usuário administrador se não existir nenhum usuário no sistema.
    """
    # Verificar se a tabela existe primeiro
    if not table_exists('usuarios'):
        logger.warning("Tabela 'usuarios' não existe para verificar usuário admin")
        return False

    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se já existe algum usuário admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'dev'")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            logger.info("Nenhum usuário administrador encontrado. Criando usuário padrão...")

            # Inserir usuário administrador
            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, senha_bruta, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "Administrador",
                "admin@vortex.com",
                "(11) 99999-9999",
                "$2b$12$uXbOUJ.KaQvp0ODJjnwES.7.mtL1Qzx3vibMGdGeDJ0ysM3dTGVJ2",  # hash para 'admin123'
                "admin123",
                "dev",
                datetime.now()
            ))
            conn.commit()
            logger.info("Usuário administrador criado com sucesso")
            return True
        else:
            logger.info(f"Já existem {admin_count} usuários administradores no sistema")
            return True
    except Exception as e:
        logger.error(f"Erro ao verificar/criar usuário administrador: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def insert_sample_products():
    """
    Insere produtos de exemplo se a tabela estiver vazia.
    """
    # Verificar se a tabela existe primeiro
    if not table_exists('produtos'):
        logger.warning("Tabela 'produtos' não existe para inserir produtos de exemplo")
        return False

    conn = get_app_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se já existem produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        product_count = cursor.fetchone()[0]

        if product_count == 0:
            logger.info("Nenhum produto encontrado. Inserindo produtos de exemplo...")

            # Lista de produtos de exemplo
            produtos_exemplo = [
                {
                    "nome": "Vinho Tinto Cabernet Sauvignon",
                    "descricao": "Vinho tinto encorpado com notas de frutas vermelhas maduras e um toque de carvalho.",
                    "preco": 89.90,
                    "quantidade_estoque": 25,
                    "imagem_url": "/static/images/produtos/vinho_tinto.jpg"
                },
                {
                    "nome": "Espumante Brut Rosé",
                    "descricao": "Espumante leve e refrescante com delicado aroma frutado e perlage fino e persistente.",
                    "preco": 69.90,
                    "quantidade_estoque": 15,
                    "imagem_url": "/static/images/produtos/espumante_rose.jpg"
                },
                {
                    "nome": "Whisky Single Malt 12 Anos",
                    "descricao": "Whisky escocês com notas de mel, caramelo e um leve toque defumado. Envelhecido por 12 anos.",
                    "preco": 289.90,
                    "quantidade_estoque": 8,
                    "imagem_url": "/static/images/produtos/whisky.jpg"
                },
                {
                    "nome": "Gin Premium London Dry",
                    "descricao": "Gin artesanal com botânicos selecionados, perfeito para drinks sofisticados.",
                    "preco": 129.90,
                    "quantidade_estoque": 12,
                    "imagem_url": "/static/images/produtos/gin.jpg"
                },
                {
                    "nome": "Cerveja IPA Artesanal",
                    "descricao": "Cerveja India Pale Ale com notas cítricas e amargor acentuado. Produção artesanal em pequenos lotes.",
                    "preco": 22.90,
                    "quantidade_estoque": 35,
                    "imagem_url": "/static/images/produtos/cerveja_ipa.jpg"
                }
            ]

            # Inserir cada produto
            for produto in produtos_exemplo:
                cursor.execute("""
                    INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    produto["nome"],
                    produto["descricao"],
                    produto["preco"],
                    produto["quantidade_estoque"],
                    produto["imagem_url"],
                    datetime.now()
                ))

            conn.commit()
            logger.info(f"Inseridos {len(produtos_exemplo)} produtos de exemplo com sucesso")
            return True
        else:
            logger.info(f"Já existem {product_count} produtos no sistema")
            return True
    except Exception as e:
        logger.error(f"Erro ao inserir produtos de exemplo: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados SQLite"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Configura o banco de dados com as tabelas necessárias"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Criar tabela de produtos se não existir
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            quantidade_estoque INTEGER DEFAULT 0,
            imagem_url TEXT
        )
        ''')
        
        # Criar tabela de movimentações de estoque se não existir
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            data TEXT NOT NULL,
            observacao TEXT,
            estoque_anterior INTEGER NOT NULL,
            estoque_atual INTEGER NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        ''')
        
        # Outras tabelas...
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar banco de dados: {str(e)}")
        return False