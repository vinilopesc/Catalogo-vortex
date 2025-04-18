"""
Entidade de domínio: Movimentacao
Representa uma movimentação de estoque no sistema.
"""

from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoMovimentacao(Enum):
    """Tipos possíveis de movimentação de estoque"""
    ENTRADA = "entrada"
    SAIDA = "saida"


@dataclass
class Movimentacao:
    """
    Entidade de Movimentação seguindo os princípios de DDD.
    Representa uma entrada ou saída de produtos no estoque.
    """
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int
    preco_unitario: float
    data: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    observacao: Optional[str] = None
    estoque_anterior: Optional[int] = None
    estoque_atual: Optional[int] = None

    def __post_init__(self):
        """Validações na criação do objeto"""
        self._validar()

    def _validar(self):
        """Aplica regras de validação da movimentação"""
        if not isinstance(self.tipo, TipoMovimentacao):
            raise ValueError(f"Tipo deve ser um TipoMovimentacao, recebido: {type(self.tipo)}")

        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        if self.preco_unitario < 0:
            raise ValueError("Preço unitário não pode ser negativo")

        if self.estoque_anterior is not None and self.estoque_atual is not None:
            # Validar consistência do estoque
            if self.tipo == TipoMovimentacao.ENTRADA:
                if self.estoque_atual != self.estoque_anterior + self.quantidade:
                    raise ValueError("Inconsistência no cálculo de estoque para entrada")
            else:  # SAIDA
                if self.estoque_atual != self.estoque_anterior - self.quantidade:
                    raise ValueError("Inconsistência no cálculo de estoque para saída")

    @property
    def valor_total(self) -> float:
        """Calcula o valor total da movimentação."""
        return self.quantidade * self.preco_unitario

    def to_dict(self) -> dict:
        """Converte a entidade para um dicionário."""
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "tipo": self.tipo.value,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "data": self.data.isoformat() if isinstance(self.data, datetime) else self.data,
            "observacao": self.observacao,
            "estoque_anterior": self.estoque_anterior,
            "estoque_atual": self.estoque_atual,
            "valor_total": self.valor_total
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Movimentacao':
        """Cria uma instância a partir de um dicionário."""
        # Converter tipo de string para enum
        tipo_str = data.get("tipo")
        tipo = TipoMovimentacao(tipo_str) if tipo_str else None

        # Converter data de string para datetime se necessário
        data_mov = data.get("data")
        if isinstance(data_mov, str):
            try:
                data_mov = datetime.fromisoformat(data_mov)
            except ValueError:
                data_mov = datetime.now()
        elif data_mov is None:
            data_mov = datetime.now()

        return cls(
            id=data.get("id"),
            produto_id=data.get("produto_id"),
            tipo=tipo,
            quantidade=data.get("quantidade"),
            preco_unitario=data.get("preco_unitario"),
            data=data_mov,
            observacao=data.get("observacao"),
            estoque_anterior=data.get("estoque_anterior"),
            estoque_atual=data.get("estoque_atual")
        )