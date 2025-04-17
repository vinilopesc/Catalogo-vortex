"""
Repositório para acesso a dados de produtos no banco de dados.
Segue o padrão Repository do DDD.
"""

import logging
from typing import List, Optional
from datetime import datetime

from backend.domain.produto import Produto
from backend.infrastructure.db_manager import execute_query

# Configurar logger
logger = logging.getLogger(__name__)


class ProdutoRepository:
    """
    Repositório para operações relacionadas a produtos.
    Segue o padrão Repository do DDD.
    """

    def __init__(self):
        """
        Inicializa o repositório.
        """
        pass

    def criar(self, produto: Produto) -> Produto:
        """
        Cria um novo produto no banco de dados.
        Retorna o produto com o ID atribuído.
        """
        try:
            query = """
                INSERT INTO produtos (
                    nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao, deletado
                ) VALUES (%s, %s, %s, %s, %s, %s, 0)
            """
            params = (
                produto.nome,
                produto.descricao,
                produto.preco,
                produto.quantidade_estoque,
                produto.imagem_url,
                datetime.now()
            )

            produto_id = execute_query(query, params)

            # Atribuir ID ao produto
            produto.id = produto_id
            logger.info(f"Produto criado com ID: {produto_id}")
            return produto

        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise Exception(f"Erro ao criar produto: {str(e)}")

    def obter_por_id(self, id: int) -> Optional[Produto]:
        """
        Busca um produto pelo ID.
        Retorna None se não encontrar ou se estiver marcado como deletado.
        """
        try:
            query = """
                SELECT * FROM produtos 
                WHERE id = %s AND (deletado = 0 OR deletado IS NULL)
            """
            result = execute_query(query, (id,), fetch=True)

            if not result:
                logger.info(f"Produto ID {id} não encontrado ou está deletado")
                return None

            # Construir objeto Produto a partir do primeiro resultado
            produto_data = result[0]
            return Produto(
                id=produto_data["id"],
                nome=produto_data["nome"],
                descricao=produto_data["descricao"],
                preco=float(produto_data["preco"]),
                quantidade_estoque=int(produto_data["quantidade_estoque"]),
                imagem_url=produto_data["imagem_url"]
            )

        except Exception as e:
            logger.error(f"Erro ao buscar produto ID {id}: {str(e)}")
            return None

    def listar_todos(self) -> List[Produto]:
        """
        Lista todos os produtos ativos (não deletados).
        """
        try:
            query = """
                SELECT * FROM produtos 
                WHERE deletado = 0 OR deletado IS NULL
                ORDER BY nome
            """
            result = execute_query(query, fetch=True)

            # Converter resultados em objetos Produto
            produtos = []
            for produto_data in result:
                try:
                    produto = Produto(
                        id=produto_data["id"],
                        nome=produto_data["nome"],
                        descricao=produto_data.get("descricao", ""),
                        preco=float(produto_data["preco"]),
                        quantidade_estoque=int(produto_data["quantidade_estoque"]),
                        imagem_url=produto_data.get("imagem_url")
                    )
                    produtos.append(produto)
                except Exception as e:
                    logger.error(f"Erro ao processar produto ID {produto_data.get('id')}: {str(e)}")

            logger.info(f"Total de produtos listados: {len(produtos)}")
            return produtos

        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            return []

    def atualizar(self, produto: Produto) -> Produto:
        """
        Atualiza um produto existente.
        """
        try:
            query = """
                UPDATE produtos 
                SET nome = %s, descricao = %s, preco = %s, 
                    quantidade_estoque = %s, imagem_url = %s
                WHERE id = %s
            """
            params = (
                produto.nome,
                produto.descricao,
                produto.preco,
                produto.quantidade_estoque,
                produto.imagem_url,
                produto.id
            )

            rows_affected = execute_query(query, params)

            # Verificar se o produto existe
            if rows_affected == 0:
                raise Exception(f"Produto com ID {produto.id} não encontrado")

            logger.info(f"Produto ID {produto.id} atualizado com sucesso")
            return produto

        except Exception as e:
            logger.error(f"Erro ao atualizar produto ID {produto.id}: {str(e)}")
            raise Exception(f"Erro ao atualizar produto: {str(e)}")

    def excluir(self, id: int) -> bool:
        """
        Marca um produto como excluído (exclusão lógica).
        """
        try:
            query = """
                UPDATE produtos 
                SET deletado = 1
                WHERE id = %s
            """
            rows_affected = execute_query(query, (id,))

            success = rows_affected > 0
            logger.info(f"Produto ID {id} {'excluído com sucesso' if success else 'não encontrado'}")
            return success

        except Exception as e:
            logger.error(f"Erro ao excluir produto ID {id}: {str(e)}")
            raise Exception(f"Erro ao excluir produto: {str(e)}")

    def restaurar(self, id: int) -> bool:
        """
        Restaura um produto que foi marcado como excluído.
        """
        try:
            query = """
                UPDATE produtos 
                SET deletado = 0
                WHERE id = %s
            """
            rows_affected = execute_query(query, (id,))

            success = rows_affected > 0
            logger.info(f"Produto ID {id} {'restaurado com sucesso' if success else 'não encontrado'}")
            return success

        except Exception as e:
            logger.error(f"Erro ao restaurar produto ID {id}: {str(e)}")
            raise Exception(f"Erro ao restaurar produto: {str(e)}")

    def obter_produto_mesmo_deletado(self, id: int) -> Optional[Produto]:
        """
        Busca um produto pelo ID, independente de estar deletado ou não.
        Útil para operações que precisam verificar a existência histórica do produto.
        """
        try:
            query = """
                SELECT * FROM produtos 
                WHERE id = %s
            """
            result = execute_query(query, (id,), fetch=True)

            if not result:
                logger.info(f"Produto ID {id} não encontrado no banco")
                return None

            # Construir objeto Produto
            produto_data = result[0]
            return Produto(
                id=produto_data["id"],
                nome=produto_data["nome"],
                descricao=produto_data.get("descricao", ""),
                preco=float(produto_data["preco"]),
                quantidade_estoque=int(produto_data["quantidade_estoque"]),
                imagem_url=produto_data.get("imagem_url")
            )

        except Exception as e:
            logger.error(f"Erro ao buscar produto (mesmo deletado) ID {id}: {str(e)}")
            return None

    def verificar_e_criar_produto_padrao(self) -> Optional[Produto]:
        """
        Verifica se existem produtos no banco e cria um produto padrão se necessário.
        """
        produtos = self.listar_todos()
        if not produtos:
            logger.warning("Nenhum produto encontrado na base. Criando produto padrão...")

            try:
                produto_padrao = Produto(
                    id=None,  # Será atribuído pelo banco
                    nome="Produto Padrão",
                    descricao="Produto padrão criado automaticamente",
                    preco=10.0,
                    quantidade_estoque=100,
                    imagem_url=None  # Usar o placeholder padrão
                )

                # Criar o produto no banco
                produto_criado = self.criar(produto_padrao)
                logger.info(f"Produto padrão criado com ID: {produto_criado.id}")
                return produto_criado

            except Exception as e:
                logger.error(f"Erro ao criar produto padrão: {str(e)}")
                return None

        return produtos[0]  # Retorna o primeiro produto encontrado