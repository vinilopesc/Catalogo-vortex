# backend/application/services/pedido_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.domain.pedido import Pedido, ItemPedido, StatusPedido
from backend.domain.cliente import Cliente
from backend.infrastructure.repositories.pedido_repository import PedidoRepository
from backend.infrastructure.repositories.produto_repository import ProdutoRepository
from backend.infrastructure.repositories.usuario_repository import UsuarioRepository


class PedidoService:
    """
    Serviço de aplicação para gerenciar pedidos.
    """

    def __init__(self):
        self.pedido_repository = PedidoRepository()
        self.produto_repository = ProdutoRepository()
        self.usuario_repository = UsuarioRepository()

    def criar_rascunho_pedido(self, cliente_id: int) -> Dict[str, Any]:
        """
        Cria um pedido em estado de rascunho (carrinho) para um cliente.
        """
        cliente = self.usuario_repository.obter_cliente_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com ID {cliente_id} não encontrado")

        pedido = Pedido(
            id=0,
            cliente=cliente,
            status=StatusPedido.CARRINHO,
            data_criacao=datetime.now()
        )

        pedido = self.pedido_repository.criar(pedido)
        return pedido.to_dict()

    def adicionar_item_ao_pedido(self, pedido_id: int, produto_id: int, quantidade: int) -> Dict[str, Any]:
        """
        Adiciona um item a um pedido existente ou atualiza a quantidade.
        """
        pedido = self.pedido_repository.obter_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

        # Verificar se o pedido está em estado que permite alterações
        if pedido.status != StatusPedido.CARRINHO:
            raise ValueError(f"Pedido não pode ser alterado no status atual: {pedido.status.value}")

        # Obter produto e verificar disponibilidade
        produto = self.produto_repository.obter_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado")

        if produto.quantidade_estoque < quantidade:
            raise ValueError(f"Estoque insuficiente. Disponível: {produto.quantidade_estoque}")

        # Criar item de pedido
        item = ItemPedido(
            produto_id=produto_id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            nome=produto.nome
        )

        # Adicionar item ao pedido
        pedido.adicionar_item(item)

        # Atualizar pedido no repositório
        pedido = self.pedido_repository.atualizar(pedido)
        return pedido.to_dict()

    def remover_item_do_pedido(self, pedido_id: int, produto_id: int) -> Dict[str, Any]:
        """
        Remove um item de um pedido.
        """
        pedido = self.pedido_repository.obter_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

        if pedido.status != StatusPedido.CARRINHO:
            raise ValueError(f"Pedido não pode ser alterado no status atual: {pedido.status.value}")

        pedido.remover_item(produto_id)
        pedido = self.pedido_repository.atualizar(pedido)
        return pedido.to_dict()

    def enviar_pedido(self, pedido_id: int, distribuidor_id: int, observacoes: Optional[str] = None) -> Dict[str, Any]:
        """
        Finaliza o pedido do cliente e envia para o distribuidor.
        """
        pedido = self.pedido_repository.obter_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

        if pedido.status != StatusPedido.CARRINHO:
            raise ValueError(f"Pedido já foi enviado ou está em outro estado: {pedido.status.value}")

        if not pedido.itens:
            raise ValueError("Pedido não possui itens")

        # Verificar se o distribuidor existe
        distribuidor = self.usuario_repository.obter_por_id(distribuidor_id)
        if not distribuidor:
            raise ValueError(f"Distribuidor com ID {distribuidor_id} não encontrado")

        # Verificar estoque atual dos itens
        for item in pedido.itens:
            produto = self.produto_repository.obter_por_id(item.produto_id)
            if not produto:
                raise ValueError(f"Produto com ID {item.produto_id} não encontrado")

            if produto.quantidade_estoque < item.quantidade:
                raise ValueError(
                    f"Estoque insuficiente para o produto '{produto.nome}'. Disponível: {produto.quantidade_estoque}")

        # Adicionar observações do cliente
        if observacoes:
            pedido.observacoes_cliente = observacoes

        # Enviar o pedido para o distribuidor
        pedido.enviar_para_distribuidor(distribuidor_id)

        # Atualizar pedido no repositório
        pedido = self.pedido_repository.atualizar(pedido)
        return pedido.to_dict()

    def atualizar_status_pedido(self, pedido_id: int, novo_status: str, observacoes: Optional[str] = None) -> Dict[
        str, Any]:
        """
        Atualiza o status de um pedido (usado pelo distribuidor).
        """
        pedido = self.pedido_repository.obter_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

        try:
            status = StatusPedido(novo_status)
        except ValueError:
            raise ValueError(f"Status inválido: {novo_status}")

        # Adicionar observações do distribuidor
        if observacoes:
            pedido.observacoes_distribuidor = observacoes

        # Atualizar status
        pedido.atualizar_status(status)

        # Se confirmado, reduzir o estoque
        if status == StatusPedido.CONFIRMADO:
            for item in pedido.itens:
                produto = self.produto_repository.obter_por_id(item.produto_id)
                if produto:
                    produto.quantidade_estoque -= item.quantidade
                    self.produto_repository.atualizar(produto)

        # Atualizar pedido no repositório
        pedido = self.pedido_repository.atualizar(pedido)
        return pedido.to_dict()

    def listar_pedidos_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos os pedidos de um cliente específico.
        """
        pedidos = self.pedido_repository.listar_por_cliente(cliente_id)
        return [pedido.to_dict() for pedido in pedidos]

    def listar_pedidos_distribuidor(self, distribuidor_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos os pedidos destinados a um distribuidor específico.
        """
        pedidos = self.pedido_repository.listar_por_distribuidor(distribuidor_id)
        return [pedido.to_dict() for pedido in pedidos]

    def obter_pedido(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de um pedido específico.
        """
        pedido = self.pedido_repository.obter_por_id(pedido_id)
        if not pedido:
            return None
        return pedido.to_dict()