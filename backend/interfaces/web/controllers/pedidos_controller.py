# backend/interfaces/web/controllers/pedidos_controller.py

@app.route('/lista_pedidos')
@requer_login
def lista_pedidos():
    """Página de listagem de pedidos"""
    # Adicionar estatísticas para o template
    try:
        pedido_service = PedidoService()
        pedidos = pedido_service.listar_pedidos()

        # Calcular estatísticas
        total_pedidos = len(pedidos)
        pedidos_pendentes = sum(1 for p in pedidos if p['status'] in
                                ['Enviado', 'Em Análise', 'Confirmado', 'Em Preparação'])
        pedidos_concluidos = sum(1 for p in pedidos if p['status'] == 'Entregue')
        pedidos_cancelados = sum(1 for p in pedidos if p['status'] in ['Cancelado', 'Recusado'])

        # Calcular valor total
        valor_total = sum(p['total'] for p in pedidos)

        estatisticas = {
            'total_pedidos': total_pedidos,
            'pedidos_pendentes': pedidos_pendentes,
            'pedidos_concluidos': pedidos_concluidos,
            'pedidos_cancelados': pedidos_cancelados,
            'valor_total': valor_total
        }

        return render_template("pedidos.html", estatisticas=estatisticas)
    except Exception as e:
        logger.error(f"Erro ao carregar página de pedidos: {str(e)}")
        return render_template("pedidos.html")