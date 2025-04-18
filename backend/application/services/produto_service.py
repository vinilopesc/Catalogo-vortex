"""
Serviço de aplicação para operações relacionadas a produtos.
Implementa a interface ProdutoServiceInterface.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename
import uuid

from backend.application.interfaces.produto_service_interface import ProdutoServiceInterface
from backend.domain.models.produto import Produto
from backend.infrastructure.repositories.produto_repository_interface import ProdutoRepositoryInterface
from backend.domain.exceptions.domain_exceptions import ProdutoNaoEncontradoException

# Configurar logger
logger = logging.getLogger(__name__)

class ProdutoService(ProdutoServiceInterface):
    """
    Serviço para gerenciamento de produtos no sistema.
    """

    def __init__(self, produto_repository: ProdutoRepositoryInterface):
        """
        Inicializa o serviço de produtos.

        Args:
            produto_repository: Repositório de produtos
        """
        self.produto_repository = produto_repository

    def listar_produtos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os produtos ativos no sistema.

        Returns:
            List[Dict[str, Any]]: Lista de produtos em formato de dicionário
        """
        try:
            logger.info("Listando todos os produtos ativos")
            produtos = self.produto_repository.listar_todos()
            return [produto.to_dict() for produto in produtos]
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            raise

    def obter_produto_por_id(self, produto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um produto pelo seu ID.

        Args:
            produto_id: ID do produto

        Returns:
            Optional[Dict[str, Any]]: Produto em formato de dicionário ou None
        """
        try:
            logger.info(f"Buscando produto com ID {produto_id}")
            produto = self.produto_repository.obter_por_id(produto_id)

            if not produto:
                logger.warning(f"Produto com ID {produto_id} não encontrado")
                return None

            return produto.to_dict()
        except Exception as e:
            logger.error(f"Erro ao obter produto {produto_id}: {str(e)}")
            raise

    def criar_produto(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo produto no sistema.

        Args:
            dados: Dados do produto a ser criado

        Returns:
            Dict[str, Any]: Produto criado com ID atribuído
        """
        try:
            logger.info(f"Criando novo produto: {dados.get('nome')}")

            # Validações
            if not dados.get('nome'):
                logger.error("Nome do produto é obrigatório")
                raise ValueError("Nome do produto é obrigatório")

            if 'preco' in dados and (not isinstance(dados['preco'], (int, float)) or dados['preco'] < 0):
                logger.error("Preço deve ser um número positivo")
                raise ValueError("Preço deve ser um número positivo")

            # Criar entidade produto
            produto = Produto(
                id=None,
                nome=dados.get('nome'),
                descricao=dados.get('descricao', ''),
                preco=float(dados.get('preco', 0)),
                quantidade_estoque=int(dados.get('quantidade_estoque', 0)),
                imagem_url=dados.get('imagem_url')
            )

            # Persistir produto
            produto_salvo = self.produto_repository.criar(produto)
            logger.info(f"Produto criado com sucesso. ID: {produto_salvo.id}")

            return produto_salvo.to_dict()
        except ValueError as e:
            logger.error(f"Erro de validação ao criar produto: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise

    def atualizar_produto(self, produto_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um produto existente.

        Args:
            produto_id: ID do produto a ser atualizado
            dados: Novos dados do produto

        Returns:
            Dict[str, Any]: Produto atualizado

        Raises:
            ProdutoNaoEncontradoException: Se o produto não existir
        """
        try:
            logger.info(f"Atualizando produto ID {produto_id}")

            # Buscar produto existente
            produto = self.produto_repository.obter_por_id(produto_id)
            if not produto:
                logger.error(f"Produto com ID {produto_id} não encontrado")
                raise ProdutoNaoEncontradoException(produto_id)

            # Atualizar apenas os campos fornecidos
            if 'nome' in dados:
                produto.nome = dados['nome']

            if 'descricao' in dados:
                produto.descricao = dados['descricao']

            if 'preco' in dados:
                produto.preco = float(dados['preco'])

            if 'quantidade_estoque' in dados:
                produto.quantidade_estoque = int(dados['quantidade_estoque'])

            if 'imagem_url' in dados:
                produto.imagem_url = dados['imagem_url']

            # Persistir alterações
            produto_atualizado = self.produto_repository.atualizar(produto)
            logger.info(f"Produto ID {produto_id} atualizado com sucesso")

            return produto_atualizado.to_dict()
        except ProdutoNaoEncontradoException:
            raise
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar produto {produto_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar produto {produto_id}: {str(e)}")
            raise

    def excluir_produto(self, produto_id: int) -> bool:
        """
        Exclui (logicamente) um produto do sistema.

        Args:
            produto_id: ID do produto a ser excluído

        Returns:
            bool: True se a exclusão foi bem-sucedida

        Raises:
            ProdutoNaoEncontradoException: Se o produto não existir
        """
        try:
            logger.info(f"Excluindo produto ID {produto_id}")

            # Verificar se o produto existe
            produto = self.produto_repository.obter_por_id(produto_id)
            if not produto:
                logger.error(f"Produto com ID {produto_id} não encontrado")
                raise ProdutoNaoEncontradoException(produto_id)

            # Excluir logicamente
            resultado = self.produto_repository.excluir(produto_id)

            if resultado:
                logger.info(f"Produto ID {produto_id} excluído com sucesso")
            else:
                logger.warning(f"Falha ao excluir produto ID {produto_id}")

            return resultado
        except ProdutoNaoEncontradoException:
            raise
        except Exception as e:
            logger.error(f"Erro ao excluir produto {produto_id}: {str(e)}")
            raise