"""
Interface para o serviço de produtos
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ProdutoServiceInterface(ABC):
    """
    Interface que define o contrato para o serviço de produtos.
    """

    @abstractmethod
    def listar_produtos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os produtos ativos.

        Returns:
            List[Dict[str, Any]]: Lista de produtos em formato de dicionário
        """
        pass

    @abstractmethod
    def obter_produto_por_id(self, produto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um produto pelo seu ID.

        Args:
            produto_id: ID do produto

        Returns:
            Optional[Dict[str, Any]]: Produto em formato de dicionário ou None
        """
        pass

    @abstractmethod
    def criar_produto(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo produto.

        Args:
            dados: Dados do produto

        Returns:
            Dict[str, Any]: Produto criado
        """
        pass

    @abstractmethod
    def atualizar_produto(self, produto_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um produto existente.

        Args:
            produto_id: ID do produto
            dados: Novos dados

        Returns:
            Dict[str, Any]: Produto atualizado
        """
        pass

    @abstractmethod
    def excluir_produto(self, produto_id: int) -> bool:
        """
        Exclui logicamente um produto.

        Args:
            produto_id: ID do produto

        Returns:
            bool: True se a exclusão foi bem-sucedida
        """
        pass