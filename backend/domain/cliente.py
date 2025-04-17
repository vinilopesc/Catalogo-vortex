"""
Entidade de domínio: Cliente
Representa um cliente que realiza pedidos no sistema.
Camada: Domain

Atributos:
- nome: str
- telefone: str
- email: str (opcional)
- endereco: dict (rua, numero, bairro, cidade, estado, complemento)
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Cliente:
    nome: str
    telefone: str
    email: Optional[str]
    endereco: dict  # Ex: {"rua": ..., "numero": ..., ...}

    def validar_endereco(self):
        campos_obrigatorios = ["rua", "numero", "bairro", "cidade", "estado"]
        for campo in campos_obrigatorios:
            if not self.endereco.get(campo):
                raise ValueError(f"Campo de endereço obrigatório ausente: {campo}")

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco
        }
