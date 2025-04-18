"""
Gerenciador de banco de dados unificado para o Catálogo Vortex.
Fornece conexões padronizadas com o MySQL para todas as partes do sistema.
"""

import logging
import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

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

def get_db_connection():
    """
    Retorna uma conexão ativa com o banco de dados MySQL.
    Esta é a única função que deve ser usada para obter conexões em todo o sistema.
    """
    try:
        # Usar configuração da variável de ambiente
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "catalogo_vortex"),
            autocommit=False,  # Controle explícito de transações
            buffered=True,     # Para garantir que todos os resultados são buscados
            charset='utf8mb4'  # Suporte completo a Unicode
        )

        # Configurar cursor para retornar dicionários
        conn.cursor_class = mysql.connector.cursor.MySQLCursorDict

        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise

def execute_query(query, params=None, fetch=False, commit=True):
    """
    Executa uma query SQL com tratamento de erros padronizado.

    Args:
        query (str): Query SQL a ser executada
        params (tuple, optional): Parâmetros para a query
        fetch (bool): Se deve buscar resultados (SELECT)
        commit (bool): Se deve fazer commit da transação

    Returns:
        list ou int: Resultados da query ou número de linhas afetadas
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    result = None

    try:
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount

        if commit:
            conn.commit()

        return result
    except Exception as e:
        if commit:
            conn.rollback()
        logger.error(f"Erro na execução da query: {str(e)}")
        logger.error(f"Query: {query}")
        logger.error(f"Parâmetros: {params}")
        raise
    finally:
        cursor.close()
        conn.close()

def table_exists(table_name):
    """
    Verifica se uma tabela específica existe no banco de dados.
    """
    query = "SHOW TABLES LIKE %s"
    results = execute_query(query, (table_name,), fetch=True)
    return len(results) > 0

def setup_database():
    """
    Configura o banco de dados com todas as tabelas necessárias.
    Deve ser chamado na inicialização do sistema.
    """
    logger.info("Iniciando verificação de banco de dados...")

    def update_pedidos_table():
        """
        Atualiza a tabela de pedidos com novos campos se necessário.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar se colunas já existem
            cursor.execute("PRAGMA table_info(pedidos)")
            colunas = {coluna[1] for coluna in cursor.fetchall()}

            # Adicionar novas colunas se não existirem
            if "status" not in colunas:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN status TEXT DEFAULT 'Carrinho'")

            if "distribuidor_id" not in colunas:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN distribuidor_id INTEGER")

            if "data_atualizacao" not in colunas:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN data_atualizacao TEXT")

            if "observacoes_cliente" not in colunas:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN observacoes_cliente TEXT")

            if "observacoes_distribuidor" not in colunas:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN observacoes_distribuidor TEXT")

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar tabela 'pedidos': {str(e)}")
            return False

    # Lista de funções de criação de tabelas a serem executadas
    create_functions = [
        create_usuarios_table,
        create_produtos_table,
        create_pedidos_table,
        create_itens_pedido_table,
        create_tokens_recuperacao_table,
        create_movimentacoes_table
    ]

    # Inicialização de dados
    init_functions = [
        create_admin_user_if_not_exists,
        insert_sample_products
    ]

    # Executar criação de tabelas
    for create_function in create_functions:
        try:
            create_function()
        except Exception as e:
            logger.error(f"Erro ao criar tabela: {str(e)}")

    # Executar inicialização de dados
    for init_function in init_functions:
        try:
            init_function()
        except Exception as e:
            logger.error(f"Erro na inicialização de dados: {str(e)}")

    logger.info("Verificação de banco de dados concluída")
    return True


def create_usuarios_table():
    """Cria a tabela de usuários se não existir"""
    if table_exists('usuarios'):
        return True

    logger.info("Criando tabela 'usuarios'...")
    query = """
        CREATE TABLE IF NOT EXISTS usuarios (
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
    """
    execute_query(query)
    logger.info("Tabela 'usuarios' criada com sucesso")
    return True

def create_produtos_table():
    """Cria a tabela de produtos se não existir"""
    if table_exists('produtos'):
        return True

    logger.info("Criando tabela 'produtos'...")
    query = """
        CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            preco DECIMAL(10, 2) NOT NULL,
            quantidade_estoque INT NOT NULL DEFAULT 0,
            imagem_url VARCHAR(255),
            data_criacao DATETIME NOT NULL,
            deletado BOOLEAN NOT NULL DEFAULT 0
        )
    """
    execute_query(query)
    logger.info("Tabela 'produtos' criada com sucesso")
    return True

def create_pedidos_table():
    """Cria a tabela de pedidos se não existir"""
    if table_exists('pedidos'):
        return True

    logger.info("Criando tabela 'pedidos'...")
    query = """
        CREATE TABLE IF NOT EXISTS pedidos (
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
    """
    execute_query(query)
    logger.info("Tabela 'pedidos' criada com sucesso")
    return True

def create_itens_pedido_table():
    """Cria a tabela de itens de pedido se não existir"""
    if table_exists('itens_pedido'):
        return True

    # Verificar se as tabelas dependentes existem
    if not table_exists('pedidos') or not table_exists('produtos'):
        logger.error("Não é possível criar tabela 'itens_pedido': tabelas dependentes inexistentes")
        return False

    logger.info("Criando tabela 'itens_pedido'...")
    query = """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT NOT NULL,
            produto_id INT NOT NULL,
            quantidade INT NOT NULL,
            preco_unitario DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """
    execute_query(query)
    logger.info("Tabela 'itens_pedido' criada com sucesso")
    return True

def create_tokens_recuperacao_table():
    """Cria a tabela de tokens de recuperação se não existir"""
    if table_exists('tokens_recuperacao'):
        return True

    # Verificar se a tabela dependente existe
    if not table_exists('usuarios'):
        logger.error("Não é possível criar tabela 'tokens_recuperacao': tabela 'usuarios' inexistente")
        return False

    logger.info("Criando tabela 'tokens_recuperacao'...")
    query = """
        CREATE TABLE IF NOT EXISTS tokens_recuperacao (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            token VARCHAR(100) NOT NULL,
            validade FLOAT NOT NULL,
            usado BOOLEAN NOT NULL DEFAULT 0,
            data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """
    execute_query(query)
    logger.info("Tabela 'tokens_recuperacao' criada com sucesso")
    return True

def create_movimentacoes_table():
    """Cria a tabela de movimentações se não existir"""
    if table_exists('movimentacoes'):
        return True

    # Verificar se a tabela dependente existe
    if not table_exists('produtos'):
        logger.error("Não é possível criar tabela 'movimentacoes': tabela 'produtos' inexistente")
        return False

    logger.info("Criando tabela 'movimentacoes'...")
    query = """
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            tipo ENUM('entrada', 'saida') NOT NULL,
            quantidade INT NOT NULL,
            preco_unitario DECIMAL(10, 2) NOT NULL,
            data DATETIME NOT NULL,
            observacao TEXT,
            estoque_anterior INT NOT NULL,
            estoque_atual INT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """
    execute_query(query)
    logger.info("Tabela 'movimentacoes' criada com sucesso")
    return True

# Funções de inicialização de dados
def create_admin_user_if_not_exists():
    """Cria um usuário administrador se não existir nenhum no sistema"""
    # Verificar se a tabela existe primeiro
    if not table_exists('usuarios'):
        logger.warning("Tabela 'usuarios' não existe para verificar usuário admin")
        return False

    try:
        # Verificar se já existe algum usuário admin
        query = "SELECT COUNT(*) as count FROM usuarios WHERE tipo = 'dev'"
        result = execute_query(query, fetch=True)
        admin_count = result[0]['count'] if result else 0

        if admin_count == 0:
            logger.info("Nenhum usuário administrador encontrado. Criando usuário padrão...")

            # Hash fixo para 'admin123'
            senha_hash = "$2b$12$uXbOUJ.KaQvp0ODJjnwES.7.mtL1Qzx3vibMGdGeDJ0ysM3dTGVJ2"

            # Inserir usuário administrador
            query = """
                INSERT INTO usuarios (nome, email, telefone, senha_hash, senha_bruta, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                "Administrador",
                "admin@vortex.com",
                "(11) 99999-9999",
                senha_hash,
                "admin123",
                "dev",
                datetime.now()
            )
            execute_query(query, params)
            logger.info("Usuário administrador criado com sucesso")
            return True
        else:
            logger.info(f"Já existem {admin_count} usuários administradores no sistema")
            return True
    except Exception as e:
        logger.error(f"Erro ao verificar/criar usuário administrador: {str(e)}")
        return False

def insert_sample_products():
    """Insere produtos de exemplo se a tabela estiver vazia"""
    # Verificar se a tabela existe primeiro
    if not table_exists('produtos'):
        logger.warning("Tabela 'produtos' não existe para inserir produtos de exemplo")
        return False

    try:
        # Verificar se já existem produtos
        query = "SELECT COUNT(*) as count FROM produtos"
        result = execute_query(query, fetch=True)
        product_count = result[0]['count'] if result else 0

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
            query = """
                INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            for produto in produtos_exemplo:
                params = (
                    produto["nome"],
                    produto["descricao"],
                    produto["preco"],
                    produto["quantidade_estoque"],
                    produto["imagem_url"],
                    datetime.now()
                )
                execute_query(query, params)

            logger.info(f"Inseridos {len(produtos_exemplo)} produtos de exemplo com sucesso")
            return True
        else:
            logger.info(f"Já existem {product_count} produtos no sistema")
            return True
    except Exception as e:
        logger.error(f"Erro ao inserir produtos de exemplo: {str(e)}")
        return False