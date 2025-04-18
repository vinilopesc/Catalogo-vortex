"""
Objeto de valor Dinheiro que representa um valor monetário.
É imutável e encapsula operações monetárias.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Dinheiro:
    """
    Objeto de valor para representar valores monetários.

    Atributos:
        valor (Decimal): O valor monetário
    """
    valor: Decimal

    def __post_init__(self):
        """Validações após inicialização"""
        # Garantir que o valor seja um Decimal com 2 casas decimais
        object.__setattr__(self, 'valor', Decimal(str(self.valor)).quantize(Decimal('0.01')))

        # Validar que o valor não é negativo
        if self.valor < 0:
            raise ValueError("Valor monetário não pode ser negativo")

    def __add__(self, other):
        """Soma dois valores monetários"""
        if isinstance(other, Dinheiro):
            return Dinheiro(self.valor + other.valor)
        return NotImplemented

    def __sub__(self, other):
        """Subtrai dois valores monetários"""
        if isinstance(other, Dinheiro):
            return Dinheiro(self.valor - other.valor)
        return NotImplemented

    def __mul__(self, multiplicador):
        """Multiplica o valor monetário por um número"""
        if isinstance(multiplicador, (int, float, Decimal)):
            return Dinheiro(self.valor * Decimal(str(multiplicador)))
        return NotImplemented

    def __str__(self):
        """Representação em string formatada como moeda"""
        return f"R$ {self.valor:.2f}"