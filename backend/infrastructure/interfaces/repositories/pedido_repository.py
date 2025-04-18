# backend/infrastructure/repositories/pedido_repository.py
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from backend.domain.models.pedido import Pedido, ItemPedido, StatusPedido
from backend.domain.models.cliente import Cliente
from backend.infrastructure.db.config_db import get_db_connection

# Configurar logger
logger = logging.getLogger(__name__)


class PedidoRepository:
    """
    Repositório para operações com pedidos no banco de dados.
    """

    def criar(self, pedido: Pedido) -> Pedido:
        """
        Cria um novo pedido no banco de dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Iniciar transação
            conn.begin()

            # Inserir pedido
            endereco_str = str(pedido.cliente.endereco) if isinstance(pedido.cliente.endereco,
                                                                      dict) else pedido.cliente.endereco

            cursor.execute("""
                INSERT INTO pedidos (
                    cliente_nome, cliente_telefone, cliente_email, cliente_endereco, 
                    status, data_pedido, data_criacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                pedido.cliente.nome,
                pedido.cliente.telefone,
                pedido.cliente.email,
                endereco_str,
                pedido.status.value,
                pedido.data_criacao.strftime('%d/%m/%Y %H:%M:%S'),
                pedido.data_criacao
            ))

            # Obter ID do pedido inserido
            pedido_id = cursor.lastrowid
            pedido.id = pedido_id

            # Inserir itens do pedido
            for item in pedido.itens:
                cursor.execute("""
                    INSERT INTO itens_pedido (
                        pedido_id, produto_id, quantidade, preco_unitario
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    pedido_id,
                    item.produto_id,
                    item.quantidade,
                    item.preco_unitario
                ))

                # Atribuir ID do item
                item.id = cursor.lastrowid
                item.pedido_id = pedido_id

            # Commit da transação
            conn.commit()
            logger.info(f"Pedido {pedido_id} criado com sucesso")

            return pedido

        except Exception as e:
            # Rollback em caso de erro
            conn.rollback()
            logger.error(f"Erro ao criar pedido: {str(e)}")
            raise

        finally:
            cursor.close()
            conn.close()

    def atualizar(self, pedido: Pedido) -> Pedido:
        """
        Atualiza um pedido existente.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Iniciar transação
            conn.begin()

            # Atualizar pedido
            endereco_str = str(pedido.cliente.endereco) if isinstance(pedido.cliente.endereco,
                                                                      dict) else pedido.cliente.endereco

            cursor.execute("""
                UPDATE pedidos SET
                    cliente_nome = %s,
                    cliente_telefone = %s,
                    cliente_email = %s,
                    cliente_endereco = %s,
                    status = %s
                WHERE id = %s
            """, (
                pedido.cliente.nome,
                pedido.cliente.telefone,
                pedido.cliente.email,
                endereco_str,
                pedido.status.value,
                pedido.id
            ))

            # Verificar se o pedido existe
            if cursor.rowcount == 0:
                conn.rollback()
                raise ValueError(f"Pedido com ID {pedido.id} não encontrado")

            # Atualizar itens - remover itens atuais
            cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (pedido.id,))

            # Inserir itens atualizados
            for item in pedido.itens:
                cursor.execute("""
                    INSERT INTO itens_pedido (
                        pedido_id, produto_id, quantidade, preco_unitario
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    pedido.id,
                    item.produto_id,
                    item.quantidade,
                    item.preco_unitario
                ))

                # Atualizar ID do item
                item.id = cursor.lastrowid

            # Commit da transação
            conn.commit()
            logger.info(f"Pedido {pedido.id} atualizado com sucesso")

            return pedido

        except Exception as e:
            # Rollback em caso de erro
            conn.rollback()
            logger.error(f"Erro ao atualizar pedido {pedido.id}: {str(e)}")
            raise

        finally:
            cursor.close()
            conn.close()

    def obter_por_id(self, pedido_id: int) -> Optional[Pedido]:
        """
        Obtém um pedido pelo ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Buscar dados do pedido
            cursor.execute("""
                SELECT * FROM pedidos
                WHERE id = %s AND deletado = 0
            """, (pedido_id,))

            pedido_data = cursor.fetchone()
            if not pedido_data:
                logger.info(f"Pedido {pedido_id} não encontrado")
                return None

            # Criar objeto Cliente
            cliente = Cliente(
                nome=pedido_data['cliente_nome'],
                telefone=pedido_data['cliente_telefone'],
                email=pedido_data['cliente_email'],
                endereco=pedido_data['cliente_endereco']
            )

            # Buscar itens do pedido
            cursor.execute("""
                SELECT ip.*, p.nome
                FROM itens_pedido ip
                LEFT JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.pedido_id = %s
            """, (pedido_id,))

            itens_data = cursor.fetchall()
            itens = []

            for item_data in itens_data:
                item = ItemPedido(
                    id=item_data['id'],
                    pedido_id=item_data['pedido_id'],
                    produto_id=item_data['produto_id'],
                    quantidade=item_data['quantidade'],
                    preco_unitario=item_data['preco_unitario'],
                    nome=item_data['nome']
                )
                itens.append(item)

            # Converter status de string para enum
            try:
                status = StatusPedido(pedido_data['status'])
            except ValueError:
                # Fallback para Pendente se o status não for reconhecido
                logger.warning(f"Status não reconhecido: {pedido_data['status']}. Usando 'Pendente'")
                status = StatusPedido.PENDENTE

            # Converter data de string para datetime
            try:
                if isinstance(pedido_data['data_pedido'], str):
                    data_parts = pedido_data['data_pedido'].split(' ')
                    data_str = data_parts[0]
                    hora_str = data_parts[1] if len(data_parts) > 1 else "00:00:00"

                    dia, mes, ano = map(int, data_str.split('/'))
                    hora, minuto, segundo = map(int, hora_str.split(':'))

                    data_criacao = datetime(ano, mes, dia, hora, minuto, segundo)
                else:
                    data_criacao = pedido_data['data_criacao']
            except (ValueError, IndexError):
                logger.warning(f"Erro ao converter data: {pedido_data['data_pedido']}. Usando data atual.")
                data_criacao = datetime.now()

            # Criar objeto Pedido
            pedido = Pedido(
                id=pedido_data['id'],
                cliente=cliente,
                itens=itens,
                status=status,
                data_criacao=data_criacao
            )

            logger.info(f"Pedido {pedido_id} obtido com sucesso")
            return pedido

        except Exception as e:
            logger.error(f"Erro ao obter pedido {pedido_id}: {str(e)}")
            raise

        finally:
            cursor.close()
            conn.close()

    def listar_todos(self) -> List[Pedido]:
        """
        Lista todos os pedidos ativos.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Buscar todos os pedidos
            cursor.execute("""
                SELECT * FROM pedidos
                WHERE deletado = 0
                ORDER BY data_criacao DESC
            """)

            pedidos_data = cursor.fetchall()
            pedidos = []

            for pedido_data in pedidos_data:
                pedido_id = pedido_data['id']

                # Criar objeto Cliente
                cliente = Cliente(
                    nome=pedido_data['cliente_nome'],
                    telefone=pedido_data['cliente_telefone'],
                    email=pedido_data['cliente_email'],
                    endereco=pedido_data['cliente_endereco']
                )

                # Buscar itens do pedido
                cursor.execute("""
                    SELECT ip.*, p.nome
                    FROM itens_pedido ip
                    LEFT JOIN produtos p ON ip.produto_id = p.id
                    WHERE ip.pedido_id = %s
                """, (pedido_id,))

                itens_data = cursor.fetchall()
                itens = []

                for item_data in itens_data:
                    item = ItemPedido(
                        id=item_data['id'],
                        pedido_id=item_data['pedido_id'],
                        produto_id=item_data['produto_id'],
                        quantidade=item_data['quantidade'],
                        preco_unitario=item_data['preco_unitario'],
                        nome=item_data['nome']
                    )
                    itens.append(item)

                # Converter status de string para enum
                try:
                    status = StatusPedido(pedido_data['status'])
                except ValueError:
                    # Fallback para Pendente se o status não for reconhecido
                    logger.warning(f"Status não reconhecido: {pedido_data['status']}. Usando 'Pendente'")
                    status = StatusPedido.PENDENTE

                # Converter data de string para datetime
                try:
                    if isinstance(pedido_data['data_pedido'], str):
                        data_parts = pedido_data['data_pedido'].split(' ')
                        data_str = data_parts[0]
                        hora_str = data_parts[1] if len(data_parts) > 1 else "00:00:00"

                        dia, mes, ano = map(int, data_str.split('/'))
                        hora, minuto, segundo = map(int, hora_str.split(':'))

                        data_criacao = datetime(ano, mes, dia, hora, minuto, segundo)
                    else:
                        data_criacao = pedido_data['data_criacao']
                except (ValueError, IndexError):
                    logger.warning(f"Erro ao converter data: {pedido_data['data_pedido']}. Usando data atual.")
                    data_criacao = datetime.now()

                # Criar objeto Pedido
                pedido = Pedido(
                    id=pedido_data['id'],
                    cliente=cliente,
                    itens=itens,
                    status=status,
                    data_criacao=data_criacao
                )

                pedidos.append(pedido)

            logger.info(f"Listados {len(pedidos)} pedidos com sucesso")
            return pedidos

        except Exception as e:
            logger.error(f"Erro ao listar pedidos: {str(e)}")
            raise

        finally:
            cursor.close()
            conn.close()