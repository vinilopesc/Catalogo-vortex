"""
Exceções específicas do domínio para o Catálogo Vortex.
"""

class DomainException(Exception):
    """Exceção base para todas as exceções de domínio"""
    pass

class EstoqueInsuficienteException(DomainException):
    """Exceção para quando não há estoque suficiente"""
    def __init__(self, produto_id, produto_nome, quantidade_solicitada, estoque_disponivel):
        self.produto_id = produto_id
        self.produto_nome = produto_nome
        self.quantidade_solicitada = quantidade_solicitada
        self.estoque_disponivel = estoque_disponivel
        message = (f"Estoque insuficiente para o produto '{produto_nome}' (ID: {produto_id}). "
                  f"Solicitado: {quantidade_solicitada}, Disponível: {estoque_disponivel}")
        super().__init__(message)

class TransicaoStatusInvalidaException(DomainException):
    """Exceção para quando uma transição de status é inválida"""
    def __init__(self, status_atual, status_novo, transicoes_permitidas):
        self.status_atual = status_atual
        self.status_novo = status_novo
        self.transicoes_permitidas = transicoes_permitidas
        message = (f"Não é possível mudar o status de '{status_atual}' para '{status_novo}'. "
                  f"Transições permitidas: {', '.join(transicoes_permitidas)}")
        super().__init__(message)

class ProdutoNaoEncontradoException(DomainException):
    """Exceção para quando um produto não é encontrado"""
    def __init__(self, produto_id):
        self.produto_id = produto_id
        message = f"Produto com ID {produto_id} não foi encontrado"
        super().__init__(message)

class PedidoNaoEncontradoException(DomainException):
    """Exceção para quando um pedido não é encontrado"""
    def __init__(self, pedido_id):
        self.pedido_id = pedido_id
        message = f"Pedido com ID {pedido_id} não foi encontrado"
        super().__init__(message)