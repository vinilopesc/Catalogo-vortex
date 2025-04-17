"""
Serviços da camada de aplicação para autenticação e gerenciamento de usuários.
Camada: Application
"""

import bcrypt
import logging
import traceback
from datetime import datetime
from backend.domain.usuario import Usuario
from backend.infrastructure.config_db import get_db_connection

# Configuração de logging
logger = logging.getLogger("usuario_services")

class AutenticarUsuarioService:
    """
    Responsável por verificar se uma credencial é válida (email/telefone e senha).
    """

    @staticmethod
    def executar(credencial: str, senha: str) -> Usuario:
        logger.info(f"Tentativa de autenticação com credencial: {credencial}")

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            logger.info("Buscando usuário no banco de dados...")
            cursor.execute("""
                SELECT * FROM usuarios WHERE email = %s OR telefone = %s
            """, (credencial, credencial))

            usuario_data = cursor.fetchone()
            conn.close()

            if not usuario_data:
                logger.warning(f"Usuário não encontrado para credencial: {credencial}")
                raise ValueError("Credenciais inválidas")

            logger.info(f"Usuário encontrado: ID {usuario_data['id']}, Email: {usuario_data['email']}")

            # Log da senha hash sem expor a senha real
            senha_hash_log = usuario_data['senha_hash'][:10] + '...' if usuario_data['senha_hash'] else None
            logger.info(f"Verificando senha contra hash: {senha_hash_log}")

            # Verificar se o hash está em formato correto
            if not usuario_data['senha_hash']:
                logger.error(f"Hash de senha vazio ou inválido para usuário ID {usuario_data['id']}")
                raise ValueError("Erro na verificação de senha: Hash inválido")

            # Debug do hash de senha
            try:
                logger.debug(f"Formato do hash de senha: {usuario_data['senha_hash'][:10]}...")

                # Converter valores para bytes se necessário
                senha_bytes = senha.encode('utf-8') if isinstance(senha, str) else senha
                hash_bytes = usuario_data['senha_hash'].encode('utf-8') if isinstance(usuario_data['senha_hash'], str) else usuario_data['senha_hash']

                logger.debug(f"Verificando senha. Tipo senha_bytes: {type(senha_bytes)}, Tipo hash_bytes: {type(hash_bytes)}")

                # Verificar senha
                senha_valida = bcrypt.checkpw(senha_bytes, hash_bytes)
                logger.info(f"Resultado da verificação de senha: {'Válida' if senha_valida else 'Inválida'}")

                if senha_valida:
                    logger.info(f"Autenticação bem-sucedida para usuário ID {usuario_data['id']}")
                    return Usuario(**usuario_data)
                else:
                    logger.warning(f"Senha incorreta para usuário ID {usuario_data['id']}")
                    raise ValueError("Credenciais inválidas")

            except Exception as e:
                logger.error(f"Erro durante verificação de senha: {str(e)}")
                logger.error(traceback.format_exc())
                raise ValueError(f"Erro na verificação de senha: {str(e)}")

        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Erro durante autenticação: {str(e)}")


def criar_usuario(nome: str, email: str, senha: str, telefone: str = None, tipo: str = 'funcionario'):
    """
    Cria um novo usuário no sistema.
    """
    logger.info(f"Iniciando criação de usuário: {email}, tipo: {tipo}")

    try:
        # Verificar se o email já existe
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        logger.info(f"Verificando se o email já existe: {email}")
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            logger.warning(f"Email já existe: {email}")
            conn.close()
            raise ValueError("Email já cadastrado")

        # Gerar hash da senha
        logger.info("Gerando hash de senha...")
        try:
            senha_bytes = senha.encode('utf-8')
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha_bytes, salt)
            senha_hash_str = senha_hash.decode('utf-8')

            # Logging do hash (parte inicial) para debug
            logger.debug(f"Hash de senha gerado: {senha_hash_str[:10]}...")
        except Exception as e:
            logger.error(f"Erro ao gerar hash de senha: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Erro ao gerar hash de senha: {str(e)}")

        # Inserir usuário
        logger.info("Inserindo usuário no banco de dados...")
        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, telefone, senha_hash, tipo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, telefone, senha_hash_str, tipo, datetime.now()))

            novo_id = cursor.lastrowid
            logger.info(f"Usuário criado com ID: {novo_id}")

            conn.commit()

            # Verificar se o usuário foi realmente criado
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (novo_id,))
            novo_usuario = cursor.fetchone()

            if not novo_usuario:
                logger.error(f"Usuário não encontrado após criação. ID: {novo_id}")
                raise ValueError("Erro ao criar usuário: não foi possível encontrar o registro após a inserção")

            logger.info(f"Usuário criado com sucesso: {novo_usuario['email']}")
            return Usuario(**novo_usuario)

        except Exception as e:
            logger.error(f"Erro ao inserir usuário no banco de dados: {str(e)}")
            logger.error(traceback.format_exc())

            try:
                conn.rollback()
                logger.info("Rollback realizado após erro")
            except:
                logger.error("Erro ao realizar rollback")

            raise ValueError(f"Erro ao criar usuário: {str(e)}")

    except Exception as e:
        logger.error(f"Erro durante criação de usuário: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Erro ao criar usuário: {str(e)}")
    finally:
        try:
            cursor.close()
            conn.close()
            logger.info("Conexão com banco de dados fechada")
        except:
            logger.error("Erro ao fechar conexão com banco de dados")


def listar_usuarios():
    """
    Retorna todos os usuários cadastrados no banco.
    """
    logger.info("Listando todos os usuários")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        logger.info("Executando query para listar usuários")
        cursor.execute("SELECT * FROM usuarios WHERE deletado = 0")
        usuarios_data = cursor.fetchall()

        logger.info(f"Encontrados {len(usuarios_data)} usuários")

        conn.close()
        logger.info("Conexão fechada")

        return [Usuario(**usuario) for usuario in usuarios_data]

    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        logger.error(traceback.format_exc())
        raise