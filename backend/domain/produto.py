"""
Módulo de entidade de domínio: Produto
Responsável por representar um produto no sistema.
Camada: Domain
Utilização: utilizada por casos de uso na camada Application

Atributos esperados:
- id: int (identificador único)
- nome: str
- descricao: str
- preco: float
- imagem_url: str (opcional)
- quantidade_estoque: int
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Produto:
    id: int
    nome: str
    descricao: str
    preco: float
    quantidade_estoque: int
    imagem_url: Optional[str] = field(default=None)

    def __post_init__(self):
        if not self.nome:
            raise ValueError("Nome do produto é obrigatório")
        if self.preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if self.quantidade_estoque < 0:
            raise ValueError("Estoque não pode ser negativo")

    def atualizar_estoque(self, quantidade: int):
        """
        Atualiza a quantidade em estoque.
        quantidade: int - valor a ser adicionado (pode ser negativo para reduzir)
        """
        novo_estoque = self.quantidade_estoque + quantidade
        if novo_estoque < 0:
            raise ValueError("Quantidade em estoque não pode ficar negativa")
        self.quantidade_estoque = novo_estoque

    def to_dict(self) -> dict:
        """Converte o produto para um dicionário serializável (ex: para API)"""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "imagem_url": self.imagem_url,
            "quantidade_estoque": self.quantidade_estoque,
        }
