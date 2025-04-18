"""
Serviço de domínio com as regras de negócio relacionadas à gestão de estoque.
"""

from backend.domain.models.produto import Produto
from backend.domain.models.movimentacao import Movimentacao, TipoMovimentacao
from backend.domain.exceptions.domain_exceptions import EstoqueInsuficienteException


class RegrasEstoque:
    """
    Serviço de domínio contendo as regras de negócio para gestão de estoque.
    """

    @staticmethod
    def validar_estoque_suficiente(produto: Produto, quantidade: int) -> bool:
        """
        Valida se o produto tem estoque suficiente para a quantidade solicitada.

        Args:
            produto: Produto a ser verificado
            quantidade: Quantidade solicitada

        Returns:
            bool: True se o estoque for suficiente

        Raises:
            EstoqueInsuficienteException: Se o estoque for insuficiente
        """
        if produto.quantidade_estoque < quantidade:
            raise EstoqueInsuficienteException(
                produto.id,
                produto.nome,
                quantidade,
                produto.quantidade_estoque
            )
        return True

    @staticmethod
    def calcular_novo_estoque(produto: Produto, tipo_movimentacao: TipoMovimentacao, quantidade: int) -> int:
        """
        Calcula o novo estoque após uma movimentação.

        Args:
            produto: Produto a ser atualizado
            tipo_movimentacao: Tipo da movimentação (entrada ou saída)
            quantidade: Quantidade da movimentação

        Returns:
            int: Novo valor do estoque
        """
        estoque_atual = produto.quantidade_estoque

        if tipo_movimentacao == TipoMovimentacao.ENTRADA:
            return estoque_atual + quantidade
        else:  # SAIDA
            novo_estoque = estoque_atual - quantidade
            if novo_estoque < 0:
                raise EstoqueInsuficienteException(
                    produto.id,
                    produto.nome,
                    quantidade,
                    estoque_atual
                )
            return novo_estoque