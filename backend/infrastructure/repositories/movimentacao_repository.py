from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

from backend.domain.entities.movimentacao import Movimentacao, TipoMovimentacao
from backend.infrastructure.db_manager import get_db_connection


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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO movimentacoes (
                    produto_id, tipo, quantidade, preco_unitario, 
                    data, observacao, estoque_anterior, estoque_atual
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movimentacao.produto_id,
                movimentacao.tipo.value,
                movimentacao.quantidade,
                movimentacao.preco_unitario,
                movimentacao.data.isoformat(),
                movimentacao.observacao,
                movimentacao.estoque_anterior,
                movimentacao.estoque_atual
            ))
            
            movimentacao.id = cursor.lastrowid
            conn.commit()
            return movimentacao
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao criar movimentação: {str(e)}")
            
        finally:
            conn.close()
    
    def obter_por_id(self, id: int) -> Optional[Movimentacao]:
        """
        Busca uma movimentação pelo ID.
        Retorna None se não encontrar.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.id = ?
            ''', (id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            # Converter para dicionário
            movimentacao_dict = {
                "id": row["id"],
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"],
                "tipo": row["tipo"],
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
                "data": row["data"],
                "observacao": row["observacao"],
                "estoque_anterior": row["estoque_anterior"],
                "estoque_atual": row["estoque_atual"]
            }
            
            return Movimentacao.from_dict(movimentacao_dict)
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao buscar movimentação: {str(e)}")
            
        finally:
            conn.close()
    
    def listar_todos(self) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações com informações do produto.
        Retorna uma lista de dicionários com os dados das movimentações.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                ORDER BY m.data DESC
            ''')
            
            movimentacoes = []
            for row in cursor.fetchall():
                movimentacao = {
                    "id": row["id"],
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "tipo": row["tipo"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                    "data": row["data"],
                    "observacao": row["observacao"],
                    "estoque_anterior": row["estoque_anterior"],
                    "estoque_atual": row["estoque_atual"]
                }
                movimentacoes.append(movimentacao)
                
            return movimentacoes
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar movimentações: {str(e)}")
            
        finally:
            conn.close()
    
    def listar_por_produto(self, produto_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações de um produto específico.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.*, p.nome as produto_nome 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.produto_id = ?
                ORDER BY m.data DESC
            ''', (produto_id,))
            
            movimentacoes = []
            for row in cursor.fetchall():
                movimentacao = {
                    "id": row["id"],
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "tipo": row["tipo"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                    "data": row["data"],
                    "observacao": row["observacao"],
                    "estoque_anterior": row["estoque_anterior"],
                    "estoque_atual": row["estoque_atual"]
                }
                movimentacoes.append(movimentacao)
                
            return movimentacoes
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar movimentações do produto: {str(e)}")
            
        finally:
            conn.close() 