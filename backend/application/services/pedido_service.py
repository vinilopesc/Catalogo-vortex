# backend/application/services/pedido_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.domain.pedido import Pedido, ItemPedido, StatusPedido
from backend.domain.cliente import Cliente
from backend.infrastructure.repositories.pedido_repository import PedidoRepository
from backend.infrastructure.repositories.produto_repository import ProdutoRepository
import logging

# Configurar logger
logger = logging.getLogger(__name__)


class PedidoService:
    """
    Serviço para gerenciar pedidos no sistema.
    """

    def __init__(self):
        self.pedido_repository = PedidoRepository()
        self.produto_repository = ProdutoRepository()

    def criar_pedido(self, dados_cliente: Dict[str, Any], itens_pedido: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cria um novo pedido com os dados do cliente e itens.
        """
        try:
            logger.info(f"Iniciando criação de pedido para cliente: {dados_cliente.get('nome')}")

            # Criar objeto Cliente
            cliente = Cliente(
                nome=dados_cliente.get('nome'),
                telefone=dados_cliente.get('telefone'),
                email=dados_cliente.get('email'),
                endereco=dados_cliente.get('endereco', {})
            )

            # Validar cliente
            if not cliente.nome or not cliente.telefone:
                logger.error("Dados do cliente incompletos")
                raise ValueError("Nome e telefone do cliente são obrigatórios")

            # Validar endereço
            try:
                cliente.validar_endereco()
            except ValueError as e:
                logger.error(f"Endereço inválido: {str(e)}")
                raise

            # Criar objeto Pedido
            pedido = Pedido(
                id=0,  # Será atribuído pelo repositório
                cliente=cliente,
                status=StatusPedido.CARRINHO,
                data_criacao=datetime.now()
            )

            # Adicionar itens ao pedido
            for item_data in itens_pedido:
                produto_id = item_data.get('id')
                quantidade = item_data.get('quantidade', 1)

                # Validar produto
                produto = self.produto_repository.obter_por_id(produto_id)
                if not produto:
                    logger.error(f"Produto não encontrado: ID {produto_id}")
                    raise ValueError(f"Produto com ID {produto_id} não encontrado")

                # Verificar estoque
                if quantidade > produto.quantidade_estoque:
                    logger.error(f"Estoque insuficiente para produto {produto.nome}")
                    raise ValueError(f"Estoque insuficiente para o produto {produto.nome}")

                # Criar e adicionar item
                item = ItemPedido(
                    produto_id=produto_id,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                    nome=produto.nome
                )
                pedido.adicionar_item(item)

            # Validar pedido
            if not pedido.itens:
                logger.error("Tentativa de criar pedido sem itens")
                raise ValueError("O pedido deve conter pelo menos um item")

            # Salvar pedido
            pedido = self.pedido_repository.criar(pedido)
            logger.info(f"Pedido criado com sucesso. ID: {pedido.id}")

            return pedido.to_dict()

        except Exception as e:
            logger.error(f"Erro ao criar pedido: {str(e)}")
            raise

    def atualizar_status_pedido(self, pedido_id: int, novo_status: str, observacoes: Optional[str] = None) -> Dict[str, Any]:
        """
        Atualiza o status de um pedido existente.
        """
        try:
            logger.info(f"Tentando atualizar status do pedido {pedido_id} para {novo_status}")

            # Obter pedido
            pedido = self.pedido_repository.obter_por_id(pedido_id)
            if not pedido:
                logger.error(f"Pedido não encontrado: ID {pedido_id}")
                raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

            # Validar novo status
            try:
                status_enum = StatusPedido(novo_status)
            except ValueError:
                logger.error(f"Status inválido: {novo_status}")
                raise ValueError(
                    f"Status '{novo_status}' inválido. Valores permitidos: {', '.join([s.value for s in StatusPedido])}")

            # Validar transição de status
            self._validar_transicao_status(pedido.status, status_enum)

            # Adicionar observações se fornecidas
            if observacoes:
                if status_enum in [StatusPedido.CANCELADO, StatusPedido.RECUSADO]:
                    pedido.observacoes_distribuidor = observacoes
                else:
                    pedido.observacoes_distribuidor = observacoes

            # Atualizar status
            pedido.atualizar_status(status_enum)

            # Se o pedido for confirmado, reduzir estoque dos produtos
            if status_enum == StatusPedido.CONFIRMADO:
                self._atualizar_estoque_para_pedido_confirmado(pedido)

            # Se o pedido for cancelado, restaurar estoque (apenas se estava confirmado)
            if status_enum == StatusPedido.CANCELADO and pedido.status == StatusPedido.CONFIRMADO:
                self._restaurar_estoque_para_pedido_cancelado(pedido)

            # Salvar pedido atualizado
            pedido = self.pedido_repository.atualizar(pedido)
            logger.info(f"Status do pedido {pedido_id} atualizado para {novo_status}")

            return pedido.to_dict()

        except Exception as e:
            logger.error(f"Erro ao atualizar status do pedido {pedido_id}: {str(e)}")
            raise

    def listar_pedidos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os pedidos no sistema.
        """
        try:
            pedidos = self.pedido_repository.listar_todos()
            return [pedido.to_dict() for pedido in pedidos]
        except Exception as e:
            logger.error(f"Erro ao listar pedidos: {str(e)}")
            raise

    def obter_pedido(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um pedido específico pelo ID.
        """
        try:
            pedido = self.pedido_repository.obter_por_id(pedido_id)
            if not pedido:
                return None
            return pedido.to_dict()
        except Exception as e:
            logger.error(f"Erro ao obter pedido {pedido_id}: {str(e)}")
            raise

    def _validar_transicao_status(self, status_atual: StatusPedido, novo_status: StatusPedido) -> None:
        """
        Valida se a transição de status é permitida.
        """
        # Definir transições permitidas
        transicoes_permitidas = {
            StatusPedido.CARRINHO: [StatusPedido.ENVIADO, StatusPedido.CANCELADO],
            StatusPedido.ENVIADO: [StatusPedido.EM_ANALISE, StatusPedido.CONFIRMADO, StatusPedido.RECUSADO],
            StatusPedido.EM_ANALISE: [StatusPedido.CONFIRMADO, StatusPedido.RECUSADO],
            StatusPedido.CONFIRMADO: [StatusPedido.EM_PREPARACAO, StatusPedido.CANCELADO],
            StatusPedido.EM_PREPARACAO: [StatusPedido.ENTREGUE, StatusPedido.CANCELADO],
            StatusPedido.ENTREGUE: [],  # Status final, sem transições permitidas
            StatusPedido.CANCELADO: [],  # Status final, sem transições permitidas
            StatusPedido.RECUSADO: []  # Status final, sem transições permitidas
        }

        # Verificar se a transição é permitida
        if novo_status not in transicoes_permitidas.get(status_atual, []):
            logger.error(f"Transição de status inválida: {status_atual.value} -> {novo_status.value}")
            raise ValueError(
                f"Não é possível mudar o status de '{status_atual.value}' para '{novo_status.value}'. " +
                f"Transições permitidas: {', '.join([s.value for s in transicoes_permitidas.get(status_atual, [])])}"
            )

    def _atualizar_estoque_para_pedido_confirmado(self, pedido: Pedido) -> None:
        """
        Atualiza o estoque dos produtos quando um pedido é confirmado.
        """
        for item in pedido.itens:
            produto = self.produto_repository.obter_por_id(item.produto_id)
            if produto:
                # Verificar estoque novamente
                if produto.quantidade_estoque < item.quantidade:
                    raise ValueError(f"Estoque insuficiente para o produto {produto.nome}")

                # Reduzir estoque
                produto.quantidade_estoque -= item.quantidade
                self.produto_repository.atualizar(produto)
                logger.info(f"Estoque do produto {produto.nome} atualizado: -{item.quantidade} unidades")

    def _restaurar_estoque_para_pedido_cancelado(self, pedido: Pedido) -> None:
        """
        Restaura o estoque dos produtos quando um pedido confirmado é cancelado.
        """
        for item in pedido.itens:
            produto = self.produto_repository.obter_por_id(item.produto_id)
            if produto:
                # Restaurar estoque
                produto.quantidade_estoque += item.quantidade
                self.produto_repository.atualizar(produto)
                logger.info(f"Estoque do produto {produto.nome} restaurado: +{item.quantidade} unidades")

    def filtrar_pedidos(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filtra pedidos de acordo com critérios específicos.
        """
        try:
            # Obter todos os pedidos
            pedidos = self.listar_pedidos()

            # Aplicar filtros
            if filtros.get('status'):
                pedidos = [p for p in pedidos if p['status'] == filtros['status']]

            if filtros.get('cliente_nome'):
                termo = filtros['cliente_nome'].lower()
                pedidos = [p for p in pedidos if termo in p['cliente']['nome'].lower()]

            if filtros.get('pedido_id'):
                pedidos = [p for p in pedidos if p['id'] == filtros['pedido_id']]

            if filtros.get('data_inicial'):
                data_inicial = datetime.fromisoformat(filtros['data_inicial'])
                pedidos = [p for p in pedidos if datetime.fromisoformat(p['data_criacao']) >= data_inicial]

            if filtros.get('data_final'):
                data_final = datetime.fromisoformat(filtros['data_final'])
                pedidos = [p for p in pedidos if datetime.fromisoformat(p['data_criacao']) <= data_final]

            # Aplicar ordenação
            ordenacao = filtros.get('ordenacao', 'data_recente')

            if ordenacao == 'data_recente':
                pedidos.sort(key=lambda p: datetime.fromisoformat(p['data_criacao']), reverse=True)
            elif ordenacao == 'data_antiga':
                pedidos.sort(key=lambda p: datetime.fromisoformat(p['data_criacao']))
            elif ordenacao == 'valor_alto':
                pedidos.sort(key=lambda p: p['total'], reverse=True)
            elif ordenacao == 'valor_baixo':
                pedidos.sort(key=lambda p: p['total'])

            return pedidos

        except Exception as e:
            logger.error(f"Erro ao filtrar pedidos: {str(e)}")
            raise

    def enviar_pedido(self, pedido_id: int, distribuidor_id: int, observacoes_cliente: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia um pedido do carrinho para o distribuidor.
        """
        try:
            logger.info(f"Enviando pedido {pedido_id} para o distribuidor {distribuidor_id}")

            # Obter pedido
            pedido = self.pedido_repository.obter_por_id(pedido_id)
            if not pedido:
                logger.error(f"Pedido não encontrado: ID {pedido_id}")
                raise ValueError(f"Pedido com ID {pedido_id} não encontrado")

            # Verificar se o pedido está no estado Carrinho
            if pedido.status != StatusPedido.CARRINHO:
                logger.error(f"Pedido {pedido_id} não está no estado Carrinho, está em {pedido.status.value}")
                raise ValueError(f"Apenas pedidos em estado Carrinho podem ser enviados")

            # Verificar se há itens no pedido
            if not pedido.itens:
                logger.error(f"Pedido {pedido_id} não possui itens")
                raise ValueError("O pedido não possui itens e não pode ser enviado")

            # Adicionar observações do cliente
            if observacoes_cliente:
                pedido.observacoes_cliente = observacoes_cliente

            # Enviar pedido para o distribuidor
            pedido.enviar_para_distribuidor(distribuidor_id)

            # Salvar pedido atualizado
            pedido = self.pedido_repository.atualizar(pedido)

            # Gerar notificação para o distribuidor
            # TODO: Implementar notificação

            logger.info(f"Pedido {pedido_id} enviado com sucesso para o distribuidor {distribuidor_id}")
            return pedido.to_dict()

        except Exception as e:
            logger.error(f"Erro ao enviar pedido {pedido_id}: {str(e)}")
            raise

    def analisar_pedido(self, pedido_id: int, usuario_id: int) -> Dict[str, Any]:
        """
        Marca um pedido como "Em Análise".
        """
        try:
            logger.info(f"Marcando pedido {pedido_id} como Em Análise")

            # Verificar permissões (apenas distribuidor pode analisar)
            # TODO: Implementar verificação de permissões

            # Atualizar status
            return self.atualizar_status_pedido(pedido_id, "Em Análise")

        except Exception as e:
            logger.error(f"Erro ao analisar pedido {pedido_id}: {str(e)}")
            raise

    def paginar_pedidos(self, pedidos: List[Dict[str, Any]], pagina: int = 1, itens_por_pagina: int = 10) -> Dict[str, Any]:
        """
        Pagina uma lista de pedidos.
        """
        total_pedidos = len(pedidos)
        total_paginas = (total_pedidos + itens_por_pagina - 1) // itens_por_pagina

        # Ajustar página solicitada
        pagina = max(1, min(pagina, total_paginas)) if total_paginas > 0 else 1

        # Calcular índices
        inicio = (pagina - 1) * itens_por_pagina
        fim = min(inicio + itens_por_pagina, total_pedidos)

        # Obter pedidos da página atual
        pedidos_pagina = pedidos[inicio:fim] if total_pedidos > 0 else []

        # Retornar resultados paginados
        return {
            'pedidos': pedidos_pagina,
            'total_pedidos': total_pedidos,
            'total_paginas': total_paginas,
            'pagina_atual': pagina,
            'itens_por_pagina': itens_por_pagina,
            'tem_proxima': pagina < total_paginas,
            'tem_anterior': pagina > 1
        }

    def _validar_disponibilidade_estoque(self, pedido: Pedido) -> bool:
        """
        Verifica se há estoque disponível para todos os itens do pedido.
        """
        for item in pedido.itens:
            produto = self.produto_repository.obter_por_id(item.produto_id)
            if not produto:
                logger.error(f"Produto não encontrado: ID {item.produto_id}")
                raise ValueError(f"Produto com ID {item.produto_id} não encontrado")

            if produto.quantidade_estoque < item.quantidade:
                logger.error(f"Estoque insuficiente para o produto {produto.nome}")
                return False

        return True
