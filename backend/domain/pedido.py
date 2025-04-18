# backend/domain/pedido.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .cliente import Cliente


class StatusPedido(Enum):
    CARRINHO = "Carrinho"
    ENVIADO = "Enviado"
    EM_ANALISE = "Em Análise"
    CONFIRMADO = "Confirmado"
    EM_PREPARACAO = "Em Preparação"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"
    RECUSADO = "Recusado"


@dataclass
class ItemPedido:
    produto_id: int
    quantidade: int
    preco_unitario: float
    pedido_id: Optional[int] = None
    id: Optional[int] = None
    nome: Optional[str] = None

    def calcular_subtotal(self) -> float:
        return self.quantidade * self.preco_unitario

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "produto_id": self.produto_id,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "nome": self.nome,
            "subtotal": self.calcular_subtotal()
        }


@dataclass
class Pedido:
    id: int
    cliente: Cliente
    itens: List[ItemPedido] = field(default_factory=list)
    status: StatusPedido = StatusPedido.CARRINHO
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: Optional[datetime] = None
    distribuidor_id: Optional[int] = None
    observacoes_cliente: Optional[str] = None
    observacoes_distribuidor: Optional[str] = None

    def calcular_total(self) -> float:
        return sum(item.calcular_subtotal() for item in self.itens)

    def atualizar_status(self, novo_status: StatusPedido):
        self.status = novo_status
        self.data_atualizacao = datetime.now()

    def adicionar_item(self, item: ItemPedido):
        # Verificar se o item já existe no pedido
        for i, existing_item in enumerate(self.itens):
            if existing_item.produto_id == item.produto_id:
                # Atualizar quantidade do item existente
                self.itens[i].quantidade += item.quantidade
                return
        # Adicionar novo item
        self.itens.append(item)

    def remover_item(self, produto_id: int):
        self.itens = [item for item in self.itens if item.produto_id != produto_id]

    def enviar_para_distribuidor(self, distribuidor_id: int):
        self.status = StatusPedido.ENVIADO
        self.distribuidor_id = distribuidor_id
        self.data_atualizacao = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente.to_dict(),
            "itens": [item.to_dict() for item in self.itens],
            "status": self.status.value,
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "distribuidor_id": self.distribuidor_id,
            "observacoes_cliente": self.observacoes_cliente,
            "observacoes_distribuidor": self.observacoes_distribuidor,
            "total": self.calcular_total()
        }