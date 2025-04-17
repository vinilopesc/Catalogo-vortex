"""
Repositório para acesso a dados de movimentações no banco de dados.
Segue o padrão Repository do DDD.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.domain.entities.movimentacao import Movimentacao, TipoMovimentacao
from backend.infrastructure.db_manager import execute_query

# Configurar logger
logger = logging.getLogger(__name__)


class MovimentacaoRepository:
    """
    Repositório para operações relacionadas a movimentações de estoque.
    Segue o padrão Repository do DDD.
    """

    def criar(self, movimentacao: Movimentacao) -> Movimentacao:
        """
        Cria uma nova movimentação no banco de dados.
        Retorna a movimentação com o ID atribuído.
        """
        try:
            query = """
                INSERT INTO movimentacoes (
                    produto_id, tipo, quantidade, preco_unitario, 
                    data, observacao, estoque_anterior, estoque_atual
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                movimentacao.produto_id,
                movimentacao.tipo.value,
                movimentacao.quantidade,
                movimentacao.preco_unitario,
                movimentacao.data,
                movimentacao.observacao,
                movimentacao.estoque_anterior,
                movimentacao.estoque_atual
            )

            movimentacao_id = execute_query(query, params)

            # Atribuir ID à movimentação
            movimentacao.id = movimentacao_id
            logger.info(f"Movimentação criada com ID: {movimentacao_id}")
            return movimentacao

        except Exception as e:
            logger.error(f"Erro ao criar movimentação: {str(e)}")
            raise Exception(f"Erro ao criar movimentação: {str(e)}")

    def obter_por_id(self, id: int) -> Optional[Movimentacao]:
        """
        Busca uma movimentação pelo ID.
        Retorna None se não encontrar.
        """
        try:
            query = """
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.id = %s
            """
            result = execute_query(query, (id,), fetch=True)

            if not result:
                logger.info(f"Movimentação ID {id} não encontrada")
                return None

            # Construir objeto Movimentacao a partir do primeiro resultado
            movimentacao_data = result[0]

            # Converter string para enum
            tipo = TipoMovimentacao(movimentacao_data["tipo"])

            # Construir objeto
            return Movimentacao(
                id=movimentacao_data["id"],
                produto_id=movimentacao_data["produto_id"],
                tipo=tipo,
                quantidade=movimentacao_data["quantidade"],
                preco_unitario=movimentacao_data["preco_unitario"],
                data=movimentacao_data["data"],
                observacao=movimentacao_data.get("observacao"),
                estoque_anterior=movimentacao_data["estoque_anterior"],
                estoque_atual=movimentacao_data["estoque_atual"]
            )

        except Exception as e:
            logger.error(f"Erro ao buscar movimentação ID {id}: {str(e)}")
            return None

    def listar_todos(self) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações com informações do produto.
        Retorna uma lista de dicionários com os dados das movimentações.
        """
        try:
            query = """
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                ORDER BY m.data DESC
            """
            result = execute_query(query, fetch=True)

            # Os resultados já estão no formato de dicionário
            logger.info(f"Total de movimentações listadas: {len(result)}")
            return result

        except Exception as e:
            logger.error(f"Erro ao listar movimentações: {str(e)}")
            return []

    def listar_por_produto(self, produto_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações de um produto específico.
        """
        try:
            query = """
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.produto_id = %s
                ORDER BY m.data DESC
            """
            result = execute_query(query, (produto_id,), fetch=True)

            # Os resultados já estão no formato de dicionário
            logger.info(f"Total de movimentações do produto {produto_id}: {len(result)}")
            return result

        except Exception as e:
            logger.error(f"Erro ao listar movimentações do produto {produto_id}: {str(e)}")
            return []