"""
Serviços da camada de aplicação para operações com pedidos.
Camada: Application
"""

from backend.domain.pedido import Pedido, ItemPedido
from backend.domain.cliente import Cliente
from backend.infrastructure.config_db import get_db_connection
from typing import List, Dict
from datetime import datetime


class CriarPedidoService:
    """
    Responsável por criar pedidos completos a partir de dados brutos (ex: request HTTP).
    """
    @staticmethod
    def executar(dados_cliente: dict, lista_produtos: List[Dict], pedido_id: int = None) -> Pedido:
        # Criar objeto Cliente
        cliente = Cliente(
            nome=dados_cliente['nome'],
            telefone=dados_cliente['telefone'],
            email=dados_cliente.get('email'),
            endereco=dados_cliente.get('endereco', {})
        )

        # Validar endereço (apenas se fornecido)
        if dados_cliente.get('endereco'):
            cliente.validar_endereco()

        if not lista_produtos:
            raise ValueError("Pedido deve conter ao menos um produto")

        # Criar objetos ItemPedido a partir da lista de produtos
        itens = []
        for item in lista_produtos:
            itens.append(ItemPedido(
                produto_id=item['id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco'],
                nome=item.get('nome')
            ))

        # Criar e retornar o objeto Pedido
        return Pedido(
            id=pedido_id or 0,
            cliente=cliente,
            itens=itens,
            status="Pendente",
            data=datetime.now().isoformat()
        )


def listar_pedidos():
    """
    Retorna todos os pedidos do banco com seus itens.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar pedidos
    cursor.execute("""
        SELECT * FROM pedidos 
        WHERE deletado = 0
        ORDER BY data_criacao DESC
    """)
    pedidos_data = cursor.fetchall()

    pedidos = []
    for pedido_data in pedidos_data:
        # Criar objeto Cliente para o pedido
        cliente = Cliente(
            nome=pedido_data['cliente_nome'],
            telefone=pedido_data['cliente_telefone'],
            email=pedido_data.get('cliente_email'),
            endereco={"endereco_completo": pedido_data.get('cliente_endereco', '')}
        )

        # Buscar itens do pedido
        cursor.execute("""
            SELECT ip.*, p.nome 
            FROM itens_pedido ip
            JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.pedido_id = %s
        """, (pedido_data['id'],))
        itens_data = cursor.fetchall()

        # Converter para objetos ItemPedido
        itens = []
        for item in itens_data:
            itens.append(ItemPedido(
                id=item['id'],
                pedido_id=item['pedido_id'],
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario'],
                nome=item.get('nome')
            ))

        # Criar objeto Pedido
        pedido = Pedido(
            id=pedido_data['id'],
            cliente=cliente,
            itens=itens,
            status=pedido_data['status'],
            data=pedido_data['data_pedido']
        )

        pedidos.append(pedido)

    cursor.close()
    conn.close()
    return pedidos


def obter_pedido(pedido_id: int):
    """
    Retorna um pedido específico pelo ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar pedido
    cursor.execute("""
        SELECT * FROM pedidos 
        WHERE id = %s AND deletado = 0
    """, (pedido_id,))
    pedido_data = cursor.fetchone()

    if not pedido_data:
        cursor.close()
        conn.close()
        return None

    # Criar objeto Cliente para o pedido
    cliente = Cliente(
        nome=pedido_data['cliente_nome'],
        telefone=pedido_data['cliente_telefone'],
        email=pedido_data.get('cliente_email'),
        endereco={"endereco_completo": pedido_data.get('cliente_endereco', '')}
    )

    # Buscar itens do pedido
    cursor.execute("""
        SELECT ip.*, p.nome 
        FROM itens_pedido ip
        JOIN produtos p ON ip.produto_id = p.id
        WHERE ip.pedido_id = %s
    """, (pedido_id,))
    itens_data = cursor.fetchall()

    # Converter para objetos ItemPedido
    itens = []
    for item in itens_data:
        itens.append(ItemPedido(
            id=item['id'],
            pedido_id=item['pedido_id'],
            produto_id=item['produto_id'],
            quantidade=item['quantidade'],
            preco_unitario=item['preco_unitario'],
            nome=item.get('nome')
        ))

    # Criar objeto Pedido
    pedido = Pedido(
        id=pedido_data['id'],
        cliente=cliente,
        itens=itens,
        status=pedido_data['status'],
        data=pedido_data['data_pedido']
    )

    cursor.close()
    conn.close()
    return pedido


def atualizar_status_pedido(pedido_id: int, novo_status: str):
    """
    Atualiza o status de um pedido.
    """
    if novo_status not in ['Pendente', 'Concluído']:
        raise ValueError("Status inválido. Deve ser 'Pendente' ou 'Concluído'")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pedidos SET status = %s
        WHERE id = %s AND deletado = 0
    """, (novo_status, pedido_id))

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise ValueError(f"Pedido {pedido_id} não encontrado ou já está excluído")

    conn.commit()
    cursor.close()
    conn.close()

    return True