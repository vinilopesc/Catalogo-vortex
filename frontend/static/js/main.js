/**
 * Arquivo JavaScript principal
 * Contém funções comuns para todas as páginas do Catálogo Vortex
 */

// Inicialização global
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    initTooltips();
    
    // Alternar modo de tema (claro/escuro) - futuro recurso
    setupThemeToggle();
    
    // Fazer com que mensagens de notificação toast sejam mostradas automaticamente
    initToasts();
});

/**
 * Inicializa tooltips do Bootstrap em toda a página
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Configura o alternador de tema claro/escuro (placeholder para recurso futuro)
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            const isDarkTheme = document.body.classList.contains('dark-theme');
            localStorage.setItem('dark-theme', isDarkTheme ? 'true' : 'false');
            
            // Atualizar ícone
            const icon = this.querySelector('i');
            if (icon) {
                if (isDarkTheme) {
                    icon.classList.remove('bi-moon');
                    icon.classList.add('bi-sun');
                } else {
                    icon.classList.remove('bi-sun');
                    icon.classList.add('bi-moon');
                }
            }
        });
        
        // Restaurar preferência de tema
        const savedTheme = localStorage.getItem('dark-theme') === 'true';
        if (savedTheme) {
            document.body.classList.add('dark-theme');
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
            }
        }
    }
}

/**
 * Inicializa os toasts para serem exibidos automaticamente
 */
function initToasts() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        }).show();
    });
}

/**
 * Função para mostrar um toast de notificação dinamicamente
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo de toast (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) return;
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
    
    // Remover o elemento depois que for escondido
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Formata um valor para o formato de moeda brasileira
 * @param {number} value - O valor a ser formatado
 * @returns {string} - Valor formatado como moeda (R$ 1.234,56)
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

/**
 * Formata uma data para o formato brasileiro
 * @param {string|Date} date - Data a ser formatada
 * @returns {string} - Data formatada (31/12/2023)
 */
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleDateString('pt-BR');
}

/**
 * Limita o tamanho de um texto e adiciona "..." no final se necessário
 * @param {string} text - Texto a ser limitado
 * @param {number} length - Comprimento máximo
 * @returns {string} - Texto limitado
 */
function truncateText(text, length = 100) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

/**
 * Converte de camelCase para texto com espaços e capitalizado
 * @param {string} text - Texto em camelCase
 * @returns {string} - Texto formatado
 */
function formatCamelCase(text) {
    if (!text) return '';
    return text
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, function(str) { return str.toUpperCase(); });
}

/**
 * Gera um ID aleatório único
 * @returns {string} - ID aleatório
 */
function generateUniqueId() {
    return 'id_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
}

/**
 * Verifica se o dispositivo é mobile
 * @returns {boolean} - Verdadeiro se for um dispositivo mobile
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
