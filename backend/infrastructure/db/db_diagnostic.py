"""
Módulo de diagnóstico para verificar e resolver problemas de conexão com o banco de dados.
"""

import os
import sys
import mysql.connector
import logging
import bcrypt
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_diagnostic.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_diagnostic")

# Carregar variáveis de ambiente
load_dotenv()


def test_connection():
    """
    Testa diferentes métodos de conexão com o banco de dados.
    """
    logger.info("=== INICIANDO TESTE DE CONEXÃO COM O BANCO DE DADOS ===")

    # Obter configurações do .env
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "catalogo_vortex")

    logger.info(f"Configurações carregadas: Host={host}, Usuário={user}, Banco={database}")

    # Métodos de conexão a serem testados
    connection_methods = [
        {
            "config": {
                "host": host,
                "user": user,
                "password": password
            },
            "description": "Conexão básica sem banco de dados"
        },
        {
            "config": {
                "host": host,
                "user": user,
                "password": password,
                "database": database
            },
            "description": "Conexão básica com banco de dados"
        },
        {
            "config": {
                "host": host,
                "user": user,
                "password": password,
                "database": database,
                "auth_plugin": "mysql_native_password"
            },
            "description": "Conexão com auth_plugin=mysql_native_password"
        },
        {
            "config": {
                "host": host,
                "user": user,
                "password": password,
                "database": database,
                "ssl_disabled": True
            },
            "description": "Conexão com SSL desabilitado"
        },
        {
            "config": {
                "host": host,
                "user": user,
                "password": password,
                "database": database,
                "auth_plugin": "mysql_native_password",
                "ssl_disabled": True
            },
            "description": "Conexão com auth_plugin e SSL desabilitado"
        }
    ]

    success_methods = []

    # Testar cada método
    for idx, method in enumerate(connection_methods):
        logger.info(f"Testando método {idx + 1}: {method['description']}")

        try:
            # Tentar estabelecer conexão
            conn = mysql.connector.connect(**method["config"])
            logger.info(f"✅ SUCESSO: Método {idx + 1} - {method['description']}")

            # Verificar se pode executar queries
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info(f"   ✅ Query de teste executada com sucesso")

                # Se tiver banco de dados especificado, verificar tabelas
                if "database" in method["config"]:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        logger.info(f"   ✅ Tabelas no banco: {[t[0] for t in tables]}")
                        cursor.close()
                    except Exception as e:
                        logger.error(f"   ❌ Erro ao listar tabelas: {str(e)}")

                success_methods.append(idx)
            except Exception as e:
                logger.error(f"   ❌ Erro ao executar query de teste: {str(e)}")

            conn.close()
        except mysql.connector.Error as err:
            logger.error(f"❌ FALHA: Método {idx + 1} - {str(err)}")

    # Resumo dos resultados
    if success_methods:
        logger.info("=== RESUMO DOS TESTES DE CONEXÃO ===")
        logger.info(f"Métodos bem-sucedidos: {[i + 1 for i in success_methods]}")

        # Sugerir a melhor configuração
        best_method = connection_methods[success_methods[0]]
        logger.info(f"Recomendação: Use o método {success_methods[0] + 1} - {best_method['description']}")

        # Sugerir modificações no config_db.py
        logger.info("Sugestão de código para config_db.py:")
        code_suggestion = f"""
def get_db_connection():
    return mysql.connector.connect(
        host="{host}",
        user="{user}",
        password="sua_senha",
        database="{database}",
"""
        # Adicionar parâmetros extras conforme o método de sucesso
        method_config = best_method["config"]
        if "auth_plugin" in method_config:
            code_suggestion += f'        auth_plugin="{method_config["auth_plugin"]}",\n'
        if "ssl_disabled" in method_config and method_config["ssl_disabled"]:
            code_suggestion += '        ssl_disabled=True,\n'

        code_suggestion += "    )"

        logger.info(code_suggestion)

        return True, best_method
    else:
        logger.error("❌ TODOS OS MÉTODOS DE CONEXÃO FALHARAM")
        logger.error("Verifique as configurações de banco de dados no arquivo .env")
        logger.error("Certifique-se de que o servidor MySQL está em execução e acessível")
        logger.error("Verifique se o usuário tem permissões adequadas")

        return False, None


def create_test_user():
    """
    Tenta criar um usuário de teste para verificar problemas com hash de senha.
    """
    logger.info("=== TENTANDO CRIAR USUÁRIO DE TESTE ===")

    # Primeiro, estabelecer conexão
    success, best_method = test_connection()
    if not success:
        logger.error("Não foi possível estabelecer conexão. Abortando criação de usuário de teste.")
        return False

    try:
        # Usar o melhor método para conectar
        conn = mysql.connector.connect(**best_method["config"])
        cursor = conn.cursor()

        # Verificar se a tabela usuarios existe
        logger.info("Verificando se a tabela 'usuarios' existe...")
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        if not cursor.fetchone():
            logger.info("Tabela 'usuarios' não existe. Criando...")
            cursor.execute("""
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
            """)
            logger.info("Tabela 'usuarios' criada com sucesso")

        # Criar usuário de teste
        logger.info("Criando usuário de teste...")

        # Testar diferentes métodos de hash
        senha = "teste123"
        senha_bytes = senha.encode('utf-8')

        # Método 1: Hash padrão
        try:
            logger.info("Método 1: Hash padrão")
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha_bytes, salt)
            senha_hash_str = senha_hash.decode('utf-8')
            logger.info(f"Hash gerado: {senha_hash_str[:10]}...")

            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, senha_bruta, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "Usuário Teste 1",
                "teste1@example.com",
                "(11) 1111-1111",
                senha_hash_str,
                senha,
                "gerente",
                datetime.now()
            ))
            logger.info("✅ Usuário teste 1 criado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário teste 1: {str(e)}")

        # Método 2: Hash em string
        try:
            logger.info("Método 2: Hash em string")
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
            logger.info(f"Hash gerado: {senha_hash[:10]}...")

            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, senha_bruta, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "Usuário Teste 2",
                "teste2@example.com",
                "(22) 2222-2222",
                senha_hash,
                senha,
                "gerente",
                datetime.now()
            ))
            logger.info("✅ Usuário teste 2 criado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário teste 2: {str(e)}")

        # Hash fixo conhecido
        try:
            logger.info("Método 3: Hash fixo conhecido")
            senha_hash = "$2b$12$uXbOUJ.KaQvp0ODJjnwES.7.mtL1Qzx3vibMGdGeDJ0ysM3dTGVJ2"  # hash para "admin123"
            logger.info(f"Hash fixo: {senha_hash[:10]}...")

            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, senha_bruta, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "Administrador Teste",
                "admin@vortex.com",
                "(00) 0000-0000",
                senha_hash,
                "admin123",
                "dev",
                datetime.now()
            ))
            logger.info("✅ Usuário admin criado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário admin: {str(e)}")

        # Verificar usuários criados
        cursor.execute("SELECT id, nome, email, senha_hash FROM usuarios")
        users = cursor.fetchall()
        logger.info(f"Usuários no banco: {len(users)}")
        for user in users:
            logger.info(
                f"  - ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Hash (início): {user[3][:10] if user[3] else None}")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Teste de criação de usuário concluído")
        return True

    except Exception as e:
        logger.error(f"Erro durante teste de criação de usuário: {str(e)}")
        logger.error(traceback.format_exc())
        return False


def run_diagnostics():
    """
    Executa todos os diagnósticos disponíveis.
    """
    logger.info("=== INICIANDO DIAGNÓSTICO COMPLETO DO BANCO DE DADOS ===")
    logger.info(f"Data e hora: {datetime.now()}")

    # Verificar variáveis de ambiente
    logger.info("Verificando variáveis de ambiente...")
    env_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", "***OCULTO***"),
        "DB_NAME": os.getenv("DB_NAME")
    }

    for var, value in env_vars.items():
        if not value:
            logger.warning(f"❌ Variável {var} não definida")
        else:
            logger.info(f"✅ Variável {var} definida: {var if var != 'DB_PASSWORD' else '***OCULTO***'}")

    # Testar conexão
    logger.info("Testando conexão com o banco de dados...")
    test_connection()

    # Testar criação de usuário
    logger.info("Testando criação de usuário...")
    create_test_user()

    logger.info("=== DIAGNÓSTICO CONCLUÍDO ===")
    logger.info("Consulte o arquivo db_diagnostic.log para detalhes completos")
    logger.info(f"Log salvo em: {os.path.abspath('db_diagnostic.log')}")


if __name__ == "__main__":
    print("Executando diagnóstico do banco de dados...")
    run_diagnostics()
    print("Diagnóstico concluído. Verifique o arquivo db_diagnostic.log para detalhes.")