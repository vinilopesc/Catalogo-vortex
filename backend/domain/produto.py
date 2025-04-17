"""
Entidade de domínio: Produto
Representa um produto no sistema.
"""

from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal

@dataclass
class Produto:
    """
    Entidade de Produto seguindo os princípios de DDD.
    Representa um produto no catálogo com validações de regras de negócio.
    """
    id: Optional[int]
    nome: str
    descricao: str
    preco: float
    quantidade_estoque: int
    imagem_url: Optional[str] = None

    def __post_init__(self):
        """Validações na criação do objeto"""
        self._validar()

    def _validar(self):
        """Aplica regras de validação do produto"""
        if not self.nome or self.nome.strip() == '':
            raise ValueError("Nome do produto é obrigatório")

        if self.preco < 0:
            raise ValueError("Preço não pode ser negativo")

        if self.quantidade_estoque < 0:
            raise ValueError("Estoque não pode ser negativo")

    def atualizar_estoque(self, quantidade: int):
        """
        Atualiza a quantidade em estoque.

        Args:
            quantidade: Valor a ser adicionado (pode ser negativo para reduzir)

        Raises:
            ValueError: Se a quantidade resultante for negativa
        """
        novo_estoque = self.quantidade_estoque + quantidade
        if novo_estoque < 0:
            raise ValueError("Quantidade em estoque não pode ficar negativa")

        self.quantidade_estoque = novo_estoque
        return self.quantidade_estoque

    def atualizar_preco(self, novo_preco: float):
        """
        Atualiza o preço do produto com validação.

        Args:
            novo_preco: Novo valor de preço

        Raises:
            ValueError: Se o preço for negativo
        """
        if novo_preco < 0:
            raise ValueError("Preço não pode ser negativo")

        self.preco = novo_preco

    @property
    def valor_em_estoque(self) -> float:
        """Calcula o valor total do produto em estoque"""
        return self.preco * self.quantidade_estoque

    @property
    def disponivel(self) -> bool:
        """Verifica se o produto está disponível (tem estoque)"""
        return self.quantidade_estoque > 0

    def to_dict(self) -> dict:
        """Converte o produto para um dicionário serializável (ex: para API)"""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "imagem_url": self.imagem_url,
            "quantidade_estoque": self.quantidade_estoque,
            "valor_em_estoque": self.valor_em_estoque,
            "disponivel": self.disponivel
        }