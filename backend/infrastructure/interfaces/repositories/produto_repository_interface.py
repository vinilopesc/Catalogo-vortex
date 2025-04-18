"""
Interface para o repositório de produtos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from backend.domain.models.produto import Produto


class ProdutoRepositoryInterface(ABC):
    """
    Interface que define o contrato para o repositório de produtos.
    """

    @abstractmethod
    def criar(self, produto: Produto) -> Produto:
        """
        Cria um novo produto no banco de dados.

        Args:
            produto: Produto a ser criado

        Returns:
            Produto: Produto criado com ID atribuído
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: int) -> Optional[Produto]:
        """
        Busca um produto pelo ID.

        Args:
            id: ID do produto

        Returns:
            Optional[Produto]: Produto encontrado ou None
        """
        pass

    @abstractmethod
    def listar_todos(self) -> List[Produto]:
        """
        Lista todos os produtos ativos.

        Returns:
            List[Produto]: Lista de produtos
        """
        pass

    @abstractmethod
    def atualizar(self, produto: Produto) -> Produto:
        """
        Atualiza um produto existente.

        Args:
            produto: Produto com os dados atualizados

        Returns:
            Produto: Produto atualizado
        """
        pass

    @abstractmethod
    def excluir(self, id: int) -> bool:
        """
        Marca um produto como excluído (exclusão lógica).

        Args:
            id: ID do produto

        Returns:
            bool: True se a exclusão foi bem-sucedida
        """
        pass