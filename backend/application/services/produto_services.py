"""
Serviços da camada de aplicação para operações com produtos.
Camada: Application
"""

from backend.domain.models.produto import Produto
from typing import List

class CadastrarProdutoService:
    """
    Responsável por cadastrar novo produto a partir de dados brutos.
    """
    @staticmethod
    def executar(produto_id: int, dados: dict) -> Produto:
        return Produto(
            id=produto_id,
            nome=dados['nome'],
            descricao=dados.get('descricao', ''),
            preco=float(dados['preco']),
            quantidade_estoque=int(dados['quantidade_estoque']),
            imagem_url=dados.get('imagem_url')
        )
