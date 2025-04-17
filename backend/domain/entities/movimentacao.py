from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class TipoMovimentacao(Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


@dataclass
class Movimentacao:
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int
    preco_unitario: float
    data: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    observacao: Optional[str] = None
    estoque_anterior: Optional[int] = None
    estoque_atual: Optional[int] = None
    
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
            "data": self.data.isoformat(),
            "observacao": self.observacao,
            "estoque_anterior": self.estoque_anterior,
            "estoque_atual": self.estoque_atual
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Movimentacao':
        """Cria uma instância a partir de um dicionário."""
        # Converter tipo de string para enum
        tipo = TipoMovimentacao(data.get("tipo"))
        
        # Converter data de string para datetime se necessário
        data_mov = data.get("data")
        if isinstance(data_mov, str):
            data_mov = datetime.fromisoformat(data_mov)
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