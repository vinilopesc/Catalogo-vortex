# backend/domain/validators.py

class PedidoValidator:
    @staticmethod
    def validar_criacao_pedido(dados_cliente, itens_pedido):
        """Valida os dados para criação de pedido"""
        erros = []

        # Validar cliente
        if not dados_cliente.get('nome'):
            erros.append("Nome do cliente é obrigatório")

        if not dados_cliente.get('telefone'):
            erros.append("Telefone do cliente é obrigatório")

        # Validar endereço
        endereco = dados_cliente.get('endereco', {})
        if not endereco.get('rua'):
            erros.append("Rua é obrigatória no endereço")

        if not endereco.get('numero'):
            erros.append("Número é obrigatório no endereço")

        if not endereco.get('bairro'):
            erros.append("Bairro é obrigatório no endereço")

        if not endereco.get('cidade'):
            erros.append("Cidade é obrigatória no endereço")

        if not endereco.get('estado'):
            erros.append("Estado é obrigatório no endereço")

        # Validar itens do pedido
        if not itens_pedido or len(itens_pedido) == 0:
            erros.append("O pedido deve ter pelo menos um item")
        else:
            for i, item in enumerate(itens_pedido):
                if not item.get('id'):
                    erros.append(f"Item {i + 1}: ID do produto é obrigatório")

                quantidade = item.get('quantidade')
                if not quantidade or quantidade <= 0:
                    erros.append(f"Item {i + 1}: Quantidade deve ser maior que zero")

        return erros