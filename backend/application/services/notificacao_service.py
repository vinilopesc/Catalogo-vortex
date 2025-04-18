# backend/application/services/notificacao_service.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificacaoService:
    """
    Serviço para gerenciar notificações no sistema.
    """

    def __init__(self):
        self.tipo_notificacoes = {
            "Enviado": {
                "titulo": "Novo Pedido Recebido",
                "mensagem": "Um novo pedido foi recebido e aguarda sua análise.",
                "icon": "inbox",
                "cor": "info"
            },
            "Em Análise": {
                "titulo": "Pedido em Análise",
                "mensagem": "Seu pedido está sendo analisado pelo distribuidor.",
                "icon": "search",
                "cor": "warning"
            },
            "Confirmado": {
                "titulo": "Pedido Confirmado",
                "mensagem": "Seu pedido foi confirmado e será preparado para entrega.",
                "icon": "check-circle",
                "cor": "primary"
            },
            "Em Preparação": {
                "titulo": "Pedido em Preparação",
                "mensagem": "Seu pedido está sendo preparado para entrega.",
                "icon": "box-seam",
                "cor": "primary"
            },
            "Entregue": {
                "titulo": "Pedido Entregue",
                "mensagem": "Seu pedido foi entregue com sucesso.",
                "icon": "truck",
                "cor": "success"
            },
            "Cancelado": {
                "titulo": "Pedido Cancelado",
                "mensagem": "Seu pedido foi cancelado.",
                "icon": "x-circle",
                "cor": "danger"
            },
            "Recusado": {
                "titulo": "Pedido Recusado",
                "mensagem": "Seu pedido foi recusado pelo distribuidor.",
                "icon": "x-circle",
                "cor": "danger"
            }
        }

    def gerar_notificacao_status_pedido(self, pedido_id, status, receptor_id):
        """
        Gera uma notificação para mudança de status de pedido.
        """
        try:
            # Obter template da notificação
            template = self.tipo_notificacoes.get(status, {
                "titulo": "Atualização de Pedido",
                "mensagem": f"O status do seu pedido foi atualizado para {status}.",
                "icon": "bell",
                "cor": "secondary"
            })

            # Criar notificação
            notificacao = {
                "usuario_id": receptor_id,
                "titulo": template["titulo"],
                "mensagem": template["mensagem"],
                "icon": template["icon"],
                "cor": template["cor"],
                "data": datetime.now(),
                "lida": False,
                "link": f"/pedido/{pedido_id}",
                "pedido_id": pedido_id
            }

            # Salvar notificação no banco
            # TODO: Implementar persistência de notificações

            logger.info(f"Notificação gerada para usuário {receptor_id} sobre pedido {pedido_id}")
            return notificacao

        except Exception as e:
            logger.error(f"Erro ao gerar notificação: {str(e)}")
            return None