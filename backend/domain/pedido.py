"""
Entidade de domínio: Pedido
Representa um pedido realizado no sistema.
Camada: Domain

Atributos:
- id: int
- cliente: Cliente
- produtos: list[dict] -> cada item: {id_produto, nome, quantidade, preco}
- status: str (Pendente, Concluído)
- data: str ou datetime
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .cliente import Cliente

@dataclass
class ItemPedido:
    """
    Representa um item individual dentro de um pedido.
    """
    produto_id: int
    quantidade: int
    preco_unitario: float
    pedido_id: Optional[int] = None
    id: Optional[int] = None
    nome: Optional[str] = None

    def calcular_subtotal(self) -> float:
        """Calcula o valor total deste item (quantidade * preço)"""
        return self.quantidade * self.preco_unitario

    def to_dict(self) -> dict:
        """Converte o item para um dicionário"""
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
    produtos: List[Dict] = field(default_factory=list)  # Pode ser lista de dicionários ou ItemPedido
    itens: List[ItemPedido] = field(default_factory=list)  # Campo adicional para itens estruturados
    status: str = "Pendente"
    data: str = field(default_factory=lambda: datetime.now().isoformat())

    def calcular_total(self) -> float:
        """Calcula o valor total do pedido"""
        # Se temos itens estruturados, usar eles
        if self.itens:
            return sum(item.calcular_subtotal() for item in self.itens)
        # Caso contrário, usar a lista de produtos
        return sum(item['quantidade'] * item['preco'] for item in self.produtos)

    def marcar_como_concluido(self):
        """Muda o status do pedido para Concluído"""
        self.status = "Concluído"

    def to_dict(self) -> dict:
        """Converte o pedido para um dicionário"""
        result = {
            "id": self.id,
            "cliente": self.cliente.to_dict(),
            "status": self.status,
            "data": self.data,
            "total": self.calcular_total()
        }

        # Incluir produtos ou itens, dependendo de qual está preenchido
        if self.itens:
            result["produtos"] = [item.to_dict() for item in self.itens]
        else:
            result["produtos"] = self.produtos

        return result