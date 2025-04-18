"""
Entidade de domínio: Usuario
Representa um usuário do sistema (funcionário, gerente, desenvolvedor).
Camada: Domain

Atributos:
- id: int
- nome: str
- email: str
- telefone: str
- senha_hash: str
- tipo: str (funcionario, gerente, dev)
"""

from dataclasses import dataclass

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    telefone: str
    senha_hash: str
    tipo: str  # 'funcionario', 'gerente', 'dev'

    def validar_tipo(self):
        tipos_validos = {"funcionario", "gerente", "dev"}
        if self.tipo not in tipos_validos:
            raise ValueError(f"Tipo de usuário inválido: {self.tipo}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "tipo": self.tipo
        }
