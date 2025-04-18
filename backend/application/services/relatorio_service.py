# backend/application/services/relatorio_service.py

class RelatorioService:
    """
    Serviço para gerar relatórios do sistema.
    """

    def __init__(self):
        self.pedido_repository = PedidoRepository()

    def gerar_relatorio_pedidos(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um relatório de pedidos com base nos filtros.
        """
        try:
            # Obter pedidos filtrados
            pedidos = self.pedido_repository.listar_todos()

            # Aplicar filtros
            if filtros.get('status'):
                pedidos = [p for p in pedidos if p.status.value == filtros['status']]

            if filtros.get('data_inicial'):
                data_inicial = datetime.fromisoformat(filtros['data_inicial'])
                pedidos = [p for p in pedidos if p.data_criacao >= data_inicial]

            if filtros.get('data_final'):
                data_final = datetime.fromisoformat(filtros['data_final'])
                pedidos = [p for p in pedidos if p.data_criacao <= data_final]

            # Calcular estatísticas
            total_pedidos = len(pedidos)

            valor_total = sum(p.calcular_total() for p in pedidos)

            # Resumo por status
            status_resumo = {}
            for status in StatusPedido:
                count = sum(1 for p in pedidos if p.status == status)
                status_resumo[status.value] = {
                    'quantidade': count,
                    'percentual': (count / total_pedidos * 100) if total_pedidos > 0 else 0
                }

            # Produtos mais pedidos
            produtos_count = {}
            for pedido in pedidos:
                for item in pedido.itens:
                    if item.produto_id in produtos_count:
                        produtos_count[item.produto_id]['quantidade'] += item.quantidade
                        produtos_count[item.produto_id]['valor'] += item.calcular_subtotal()
                    else:
                        produtos_count[item.produto_id] = {
                            'id': item.produto_id,
                            'nome': item.nome or f"Produto {item.produto_id}",
                            'quantidade': item.quantidade,
                            'valor': item.calcular_subtotal()
                        }

            # Ordenar por quantidade (mais pedidos primeiro)
            produtos_populares = sorted(
                produtos_count.values(),
                key=lambda x: x['quantidade'],
                reverse=True
            )

            # Retornar relatório
            return {
                'periodo': {
                    'inicio': filtros.get('data_inicial'),
                    'fim': filtros.get('data_final')
                },
                'total_pedidos': total_pedidos,
                'valor_total': valor_total,
                'status_resumo': status_resumo,
                'produtos_populares': produtos_populares[:10]  # Top 10
            }

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de pedidos: {str(e)}")
            raise