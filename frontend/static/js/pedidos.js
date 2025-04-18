// frontend/static/js/pedidos.js

/**
 * Atualiza o status de um pedido com animação de feedback
 */
async function atualizarStatusPedido(pedidoId, novoStatus, observacoes = '') {
    try {
        // Mostrar indicador de carregamento
        const btnStatus = document.querySelector(`.btn-status-${pedidoId}`);
        const textoOriginal = btnStatus.innerHTML;
        btnStatus.disabled = true;
        btnStatus.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Atualizando...';

        // Enviar requisição para a API
        const response = await fetch(`/api/pedidos/${pedidoId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: novoStatus,
                observacoes: observacoes
            })
        });

        if (!response.ok) {
            const erro = await response.json();
            throw new Error(erro.erro || 'Erro ao atualizar status');
        }

        // Obter resposta
        const data = await response.json();

        // Atualizar UI com animação
        const pedidoRow = document.querySelector(`.pedido-row-${pedidoId}`);
        pedidoRow.classList.add('status-updated');

        // Atualizar texto de status
        const statusBadge = document.querySelector(`.status-badge-${pedidoId}`);
        statusBadge.textContent = novoStatus;
        statusBadge.className = `status-badge status-badge-${pedidoId} status-${novoStatus.toLowerCase().replace(' ', '-')}`;

        // Atualizar botões disponíveis
        atualizarBotoesStatus(pedidoId, novoStatus);

        // Mostrar mensagem de sucesso
        mostrarNotificacao('success', `Pedido atualizado para "${novoStatus}" com sucesso`);

        // Remover classe de animação após alguns segundos
        setTimeout(() => {
            pedidoRow.classList.remove('status-updated');
        }, 3000);

        // Atualizar estatísticas se necessário
        atualizarEstatisticas();

    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('error', error.message);

        // Restaurar botão
        const btnStatus = document.querySelector(`.btn-status-${pedidoId}`);
        btnStatus.disabled = false;
        btnStatus.innerHTML = textoOriginal;
    }
}

/**
 * Mostra uma notificação visual para o usuário
 */
function mostrarNotificacao(tipo, mensagem) {
    // Criar elemento toast
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${tipo === 'success' ? 'success' : tipo === 'error' ? 'danger' : 'primary'} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${mensagem}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
        </div>
    `;

    // Adicionar à página
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        const newContainer = document.createElement('div');
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(newContainer);
        newContainer.appendChild(toastEl);
    } else {
        toastContainer.appendChild(toastEl);
    }

    // Mostrar toast
    const toast = new bootstrap.Toast(toastEl, {
        delay: 5000
    });
    toast.show();

    // Remover após fechar
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}