from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

from backend.domain.produto import Produto
from backend.infrastructure.db_manager import get_db_connection


class ProdutoRepository:
    """
    Repositório para operações relacionadas a produtos.
    Segue o padrão Repository do DDD.
    """
    
    def __init__(self):
        """
        Inicializa o repositório e verifica se a coluna 'deletado' existe.
        Se não existir, adiciona a coluna à tabela produtos.
        """
        self._verificar_coluna_deletado()
    
    def _verificar_coluna_deletado(self):
        """
        Verifica se a coluna 'deletado' existe na tabela produtos.
        Se não existir, adiciona a coluna com valor padrão 0 (não deletado).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna existe na tabela
            cursor.execute("PRAGMA table_info(produtos)")
            colunas = cursor.fetchall()
            
            # Verificar se a coluna 'deletado' já existe
            coluna_deletado_existe = any(col[1] == 'deletado' for col in colunas)
            
            if not coluna_deletado_existe:
                # Adicionar a coluna 'deletado' com valor padrão 0
                cursor.execute("ALTER TABLE produtos ADD COLUMN deletado INTEGER DEFAULT 0")
                conn.commit()
        except sqlite3.Error as e:
            # Apenas logamos o erro, não interrompemos a execução
            print(f"Aviso: Não foi possível verificar/adicionar coluna 'deletado': {str(e)}")
        finally:
            conn.close()
    
    def criar(self, produto: Produto) -> Produto:
        """
        Cria um novo produto no banco de dados.
        Retorna o produto com o ID atribuído.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO produtos (
                    nome, descricao, preco, quantidade_estoque, imagem_url, deletado
                ) VALUES (?, ?, ?, ?, ?, 0)
            ''', (
                produto.nome,
                produto.descricao,
                produto.preco,
                produto.quantidade_estoque,
                produto.imagem_url
            ))
            
            produto_id = cursor.lastrowid
            conn.commit()
            
            # Atribuir ID ao produto
            produto.id = produto_id
            return produto
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao criar produto: {str(e)}")
            
        finally:
            conn.close()
    
    def obter_por_id(self, id: int) -> Optional[Produto]:
        """
        Busca um produto pelo ID.
        Retorna None se não encontrar ou se estiver marcado como deletado.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Primeiro tentamos encontrar o produto independente de estar deletado ou não
            cursor.execute('''
                SELECT * FROM produtos 
                WHERE id = ?
            ''', (id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Verificamos se o produto está marcado como deletado
            try:
                deletado = row["deletado"]
                if deletado == 1:
                    return None  # Produto marcado como deletado
            except (IndexError, KeyError):
                # A coluna 'deletado' pode não existir ainda, então ignoramos o erro
                pass
                
            # Construir objeto Produto
            return Produto(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"],
                preco=float(row["preco"]),
                quantidade_estoque=int(row["quantidade_estoque"]),
                imagem_url=row["imagem_url"]
            )
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao buscar produto: {str(e)}")
            
        finally:
            conn.close()
    
    def listar_todos(self) -> List[Produto]:
        """
        Lista todos os produtos ativos (não deletados).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Tentamos filtrar por deletado=0, mas a coluna pode não existir
            try:
                cursor.execute('''
                    SELECT * FROM produtos 
                    WHERE deletado = 0
                    ORDER BY nome
                ''')
            except sqlite3.OperationalError:
                # Se a coluna não existir, listamos todos
                cursor.execute('''
                    SELECT * FROM produtos 
                    ORDER BY nome
                ''')
            
            produtos = []
            for row in cursor.fetchall():
                produto = Produto(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    preco=float(row["preco"]),
                    quantidade_estoque=int(row["quantidade_estoque"]),
                    imagem_url=row["imagem_url"]
                )
                produtos.append(produto)
                
            return produtos
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar produtos: {str(e)}")
            
        finally:
            conn.close()
    
    def atualizar(self, produto: Produto) -> Produto:
        """
        Atualiza um produto existente.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE produtos 
                SET nome = ?, descricao = ?, preco = ?, 
                    quantidade_estoque = ?, imagem_url = ?
                WHERE id = ?
            ''', (
                produto.nome,
                produto.descricao,
                produto.preco,
                produto.quantidade_estoque,
                produto.imagem_url,
                produto.id
            ))
            
            # Verificar se o produto existe
            if cursor.rowcount == 0:
                raise Exception(f"Produto com ID {produto.id} não encontrado")
                
            conn.commit()
            return produto
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar produto: {str(e)}")
            
        finally:
            conn.close()
    
    def excluir(self, id: int) -> bool:
        """
        Marca um produto como excluído (exclusão lógica).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Tentamos atualizar o campo deletado
            try:
                cursor.execute('''
                    UPDATE produtos 
                    SET deletado = 1
                    WHERE id = ?
                ''', (id,))
            except sqlite3.OperationalError:
                # Se a coluna não existir, fazemos exclusão física
                cursor.execute('''
                    DELETE FROM produtos 
                    WHERE id = ?
                ''', (id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao excluir produto: {str(e)}")
            
        finally:
            conn.close()
            
    def restaurar(self, id: int) -> bool:
        """
        Restaura um produto que foi marcado como excluído.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE produtos 
                SET deletado = 0
                WHERE id = ?
            ''', (id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao restaurar produto: {str(e)}")
            
        finally:
            conn.close()
            
    def obter_produto_mesmo_deletado(self, id: int) -> Optional[Produto]:
        """
        Busca um produto pelo ID, independente de estar deletado ou não.
        Útil para operações que precisam verificar a existência histórica do produto.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM produtos 
                WHERE id = ?
            ''', (id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            # Construir objeto Produto
            return Produto(
                id=row["id"],
                nome=row["nome"],
                descricao=row["descricao"],
                preco=float(row["preco"]),
                quantidade_estoque=int(row["quantidade_estoque"]),
                imagem_url=row["imagem_url"]
            )
            
        except sqlite3.Error as e:
            raise Exception(f"Erro ao buscar produto: {str(e)}")
            
        finally:
            conn.close() 