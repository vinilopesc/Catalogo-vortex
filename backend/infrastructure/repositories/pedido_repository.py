# backend/infrastructure/repositories/pedido_repository.py

from typing import List, Optional
import sqlite3
from datetime import datetime

from backend.domain.pedido import Pedido, ItemPedido, StatusPedido
from backend.domain.cliente import Cliente
from backend.infrastructure.db_manager import get_db_connection


class PedidoRepository:
    """
    Repositório para operações relacionadas a pedidos.
    """

    def criar(self, pedido: Pedido) -> Pedido:
        """
        Cria um novo pedido no banco de dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Inserir pedido
            cursor.execute('''
                INSERT INTO pedidos (
                    cliente_nome, cliente_telefone, cliente_email, cliente_endereco, 
                    status, data_pedido, distribuidor_id, data_atualizacao,
                    observacoes_cliente, observacoes_distribuidor
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido.cliente.nome,
                pedido.cliente.telefone,
                pedido.cliente.email,
                str(pedido.cliente.endereco),
                pedido.status.value,
                pedido.data_criacao.isoformat(),
                pedido.distribuidor_id,
                pedido.data_atualizacao.isoformat() if pedido.data_atualizacao else None,
                pedido.observacoes_cliente,
                pedido.observacoes_distribuidor
            ))

            pedido_id = cursor.lastrowid
            pedido.id = pedido_id

            # Inserir itens do pedido se houver
            for item in pedido.itens:
                cursor.execute('''
                    INSERT INTO itens_pedido (
                        pedido_id, produto_id, quantidade, preco_unitario
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    pedido_id,
                    item.produto_id,
                    item.quantidade,
                    item.preco_unitario
                ))

                item.pedido_id = pedido_id
                item.id = cursor.lastrowid

            conn.commit()
            return pedido

        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao criar pedido: {str(e)}")

        finally:
            conn.close()

    def atualizar(self, pedido: Pedido) -> Pedido:
        """
        Atualiza um pedido existente.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Atualizar pedido
            cursor.execute('''
                UPDATE pedidos SET
                    cliente_nome = ?,
                    cliente_telefone = ?,
                    cliente_email = ?,
                    cliente_endereco = ?,
                    status = ?,
                    distribuidor_id = ?,
                    data_atualizacao = ?,
                    observacoes_cliente = ?,
                    observacoes_distribuidor = ?
                WHERE id = ?
            ''', (
                pedido.cliente.nome,
                pedido.cliente.telefone,
                pedido.cliente.email,
                str(pedido.cliente.endereco),
                pedido.status.value,
                pedido.distribuidor_id,
                pedido.data_atualizacao.isoformat() if pedido.data_atualizacao else None,
                pedido.observacoes_cliente,
                pedido.observacoes_distribuidor,
                pedido.id
            ))

            # Remover itens antigos
            cursor.execute('DELETE FROM itens_pedido WHERE pedido_id = ?', (pedido.id,))

            # Inserir itens atualizados
            for item in pedido.itens:
                cursor.execute('''
                    INSERT INTO itens_pedido (
                        pedido_id, produto_id, quantidade, preco_unitario
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    pedido.id,
                    item.produto_id,
                    item.quantidade,
                    item.preco_unitario
                ))

                item.pedido_id = pedido.id
                item.id = cursor.lastrowid

            conn.commit()
            return pedido

        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar pedido: {str(e)}")

        finally:
            conn.close()

    def obter_por_id(self, id: int) -> Optional[Pedido]:
        """
        Obtém um pedido pelo ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT * FROM pedidos WHERE id = ? AND deletado = 0
            ''', (id,))

            pedido_data = cursor.fetchone()
            if not pedido_data:
                return None

            # Criar cliente
            cliente = Cliente(
                nome=pedido_data['cliente_nome'],
                telefone=pedido_data['cliente_telefone'],
                email=pedido_data['cliente_email'],
                endereco=eval(pedido_data['cliente_endereco']) if pedido_data['cliente_endereco'] else {}
            )

            # Obter itens do pedido
            cursor.execute('''
                SELECT ip.*, p.nome 
                FROM itens_pedido ip
                LEFT JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.pedido_id = ?
            ''', (id,))

            itens_data = cursor.fetchall()
            itens = []

            for item_data in itens_data:
                itens.append(ItemPedido(
                    id=item_data['id'],
                    pedido_id=item_data['pedido_id'],
                    produto_id=item_data['produto_id'],
                    quantidade=item_data['quantidade'],
                    preco_unitario=item_data['preco_unitario'],
                    nome=item_data['nome']
                ))

            # Criar pedido
            pedido = Pedido(
                id=pedido_data['id'],
                cliente=cliente,
                itens=itens,
                status=StatusPedido(pedido_data['status']),
                data_criacao=datetime.fromisoformat(pedido_data['data_pedido']),
                data_atualizacao=datetime.fromisoformat(pedido_data['data_atualizacao']) if pedido_data[
                    'data_atualizacao'] else None,
                distribuidor_id=pedido_data['distribuidor_id'],
                observacoes_cliente=pedido_data['observacoes_cliente'],
                observacoes_distribuidor=pedido_data['observacoes_distribuidor']
            )

            return pedido

        except Exception as e:
            raise Exception(f"Erro ao obter pedido: {str(e)}")

        finally:
            conn.close()

    def listar_por_cliente(self, cliente_id: int) -> List[Pedido]:
        """
        Lista todos os pedidos de um cliente.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Obter usuário para extrair nome/telefone
            cursor.execute('''
                SELECT * FROM usuarios WHERE id = ?
            ''', (cliente_id,))

            usuario = cursor.fetchone()
            if not usuario:
                return []

            # Buscar pedidos do cliente
            cursor.execute('''
                SELECT * FROM pedidos 
                WHERE cliente_nome = ? AND cliente_telefone = ? AND deletado = 0
                ORDER BY data_pedido DESC
            ''', (usuario['nome'], usuario['telefone']))

            pedidos_data = cursor.fetchall()
            pedidos = []

            for pedido_data in pedidos_data:
                # Criar cliente
                cliente = Cliente(
                    nome=pedido_data['cliente_nome'],
                    telefone=pedido_data['cliente_telefone'],
                    email=pedido_data['cliente_email'],
                    endereco=eval(pedido_data['cliente_endereco']) if pedido_data['cliente_endereco'] else {}
                )

                # Obter itens do pedido
                cursor.execute('''
                    SELECT ip.*, p.nome 
                    FROM itens_pedido ip
                    LEFT JOIN produtos p ON ip.produto_id = p.id
                    WHERE ip.pedido_id = ?
                ''', (pedido_data['id'],))

                itens_data = cursor.fetchall()
                itens = []

                for item_data in itens_data:
                    itens.append(ItemPedido(
                        id=item_data['id'],
                        pedido_id=item_data['pedido_id'],
                        produto_id=item_data['produto_id'],
                        quantidade=item_data['quantidade'],
                        preco_unitario=item_data['preco_unitario'],
                        nome=item_data['nome']
                    ))

                # Criar pedido
                pedido = Pedido(
                    id=pedido_data['id'],
                    cliente=cliente,
                    itens=itens,
                    status=StatusPedido(pedido_data['status']),
                    data_criacao=datetime.fromisoformat(pedido_data['data_pedido']),
                    data_atualizacao=datetime.fromisoformat(pedido_data['data_atualizacao']) if pedido_data[
                        'data_atualizacao'] else None,
                    distribuidor_id=pedido_data['distribuidor_id'],
                    observacoes_cliente=pedido_data['observacoes_cliente'],
                    observacoes_distribuidor=pedido_data['observacoes_distribuidor']
                )

                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            raise Exception(f"Erro ao listar pedidos do cliente: {str(e)}")

        finally:
            conn.close()

    def listar_por_distribuidor(self, distribuidor_id: int) -> List[Pedido]:
        """
        Lista todos os pedidos destinados a um distribuidor.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT * FROM pedidos 
                WHERE distribuidor_id = ? AND deletado = 0
                ORDER BY data_pedido DESC
            ''', (distribuidor_id,))

            pedidos_data = cursor.fetchall()
            pedidos = []

            for pedido_data in pedidos_data:
                # Criar cliente
                cliente = Cliente(
                    nome=pedido_data['cliente_nome'],
                    telefone=pedido_data['cliente_telefone'],
                    email=pedido_data['cliente_email'],
                    endereco=eval(pedido_data['cliente_endereco']) if pedido_data['cliente_endereco'] else {}
                )

                # Obter itens do pedido
                cursor.execute('''
                    SELECT ip.*, p.nome 
                    FROM itens_pedido ip
                    LEFT JOIN produtos p ON ip.produto_id = p.id
                    WHERE ip.pedido_id = ?
                ''', (pedido_data['id'],))

                itens_data = cursor.fetchall()
                itens = []

                for item_data in itens_data:
                    itens.append(ItemPedido(
                        id=item_data['id'],
                        pedido_id=item_data['pedido_id'],
                        produto_id=item_data['produto_id'],
                        quantidade=item_data['quantidade'],
                        preco_unitario=item_data['preco_unitario'],
                        nome=item_data['nome']
                    ))

                # Criar pedido
                pedido = Pedido(
                    id=pedido_data['id'],
                    cliente=cliente,
                    itens=itens,
                    status=StatusPedido(pedido_data['status']),
                    data_criacao=datetime.fromisoformat(pedido_data['data_pedido']),
                    data_atualizacao=datetime.fromisoformat(pedido_data['data_atualizacao']) if pedido_data[
                        'data_atualizacao'] else None,
                    distribuidor_id=pedido_data['distribuidor_id'],
                    observacoes_cliente=pedido_data['observacoes_cliente'],
                    observacoes_distribuidor=pedido_data['observacoes_distribuidor']
                )

                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            raise Exception(f"Erro ao listar pedidos do distribuidor: {str(e)}")

        finally:
            conn.close()