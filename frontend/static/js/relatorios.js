/**
 * Relatórios - Catálogo Vortex
 * JavaScript para funcionalidades da página de relatórios
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Módulo de relatórios carregado');

    // Elementos da interface
    const filtrosForm = document.getElementById('filtros-form');
    const resetFiltrosBtn = document.getElementById('reset-filtros');
    const chartContainers = document.querySelectorAll('.chart-container');
    const datePickers = document.querySelectorAll('.date-picker');
    
    // Inicialização de gráficos de demonstração quando a página estiver totalmente carregada
    if (chartContainers.length > 0) {
        initDemoCharts();
    }
    
    // Inicializar seletores de data
    if (datePickers.length > 0) {
        initDatePickers();
    }
    
    // Inicialização dos dados da tabela
    updateReportTable();
    
    // Event listeners
    if (filtrosForm) {
        filtrosForm.addEventListener('submit', handleFiltrosSubmit);
    }
    
    if (resetFiltrosBtn) {
        resetFiltrosBtn.addEventListener('click', resetFiltros);
    }
    
    // Botões de demonstração de tipos de relatórios
    setupDemoButtons();
});

/**
 * Inicializa os seletores de data
 */
function initDatePickers() {
    // Implementação de seletores de data será adicionada posteriormente
    console.log('Inicializando seletores de data');
}

/**
 * Manipulador do envio do formulário de filtros
 * @param {Event} e - Evento de submit
 */
function handleFiltrosSubmit(e) {
    e.preventDefault();
    
    // Mostrar spinner de carregamento
    const reportBody = document.querySelector('.report-body');
    if (reportBody) {
        reportBody.innerHTML = `
            <div class="spinner-container py-5">
                <div class="spinner-grow text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-3">Gerando relatório...</p>
            </div>
        `;
    }
    
    // Simular carregamento do relatório (para fins de demonstração)
    setTimeout(() => {
        // Em uma implementação real, aqui recuperaríamos os dados do servidor
        // e atualizaríamos os gráficos e tabelas
        initDemoCharts();
        updateReportTable();
    }, 1500);
}

/**
 * Resetar filtros do formulário
 */
function resetFiltros() {
    const filtrosForm = document.getElementById('filtros-form');
    if (filtrosForm) {
        filtrosForm.reset();
    }
}

/**
 * Inicializa gráficos de demonstração
 */
function initDemoCharts() {
    // Aqui usaríamos uma biblioteca como Chart.js para gerar gráficos
    // Para fins de demonstração, mostraremos uma mensagem
    
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        const chartBody = container.querySelector('.chart-body');
        const chartType = container.dataset.chartType || 'bar';
        
        if (chartBody) {
            chartBody.innerHTML = `
                <div class="p-4 text-center">
                    <i class="bi bi-bar-chart-fill text-primary" style="font-size: 4rem; opacity: 0.7;"></i>
                    <p class="mt-3">Visualização de gráfico ${chartType} (em desenvolvimento)</p>
                </div>
            `;
        }
    });
}

/**
 * Atualiza a tabela de relatório com dados de exemplo
 */
function updateReportTable() {
    const tableBody = document.querySelector('.report-table tbody');
    if (!tableBody) return;
    
    // Limpar tabela existente
    tableBody.innerHTML = '';
    
    // Adicionar linhas de exemplo
    const demoData = [
        { produto: 'Hambúrguer Artesanal', vendas: 253, receita: 'R$ 5.060,00', crescimento: '+15%' },
        { produto: 'Pizza Margherita', vendas: 187, receita: 'R$ 4.675,00', crescimento: '+8%' },
        { produto: 'Salada Caesar', vendas: 95, receita: 'R$ 1.425,00', crescimento: '+12%' },
        { produto: 'Refrigerante Cola', vendas: 320, receita: 'R$ 1.600,00', crescimento: '+5%' },
        { produto: 'Sobremesa Brownie', vendas: 142, receita: 'R$ 1.420,00', crescimento: '+20%' },
    ];
    
    demoData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.produto}</td>
            <td class="text-center">${item.vendas}</td>
            <td class="text-end">${item.receita}</td>
            <td class="text-end text-success">${item.crescimento}</td>
        `;
        tableBody.appendChild(row);
    });
    
    // Atualizar cards de resumo
    updateSummaryCards(demoData);
}

/**
 * Atualiza os cards de resumo com valores calculados
 * @param {Array} data - Dados de relatório
 */
function updateSummaryCards(data) {
    // Calcular totais
    const totalVendas = data.reduce((sum, item) => sum + item.vendas, 0);
    const totalReceita = 'R$ ' + (data.reduce((sum, item) => {
        const valor = parseFloat(item.receita.replace('R$ ', '').replace('.', '').replace(',', '.'));
        return sum + valor;
    }, 0)).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    // Atualizar elementos
    const vendasEl = document.querySelector('[data-summary="vendas"]');
    const receitaEl = document.querySelector('[data-summary="receita"]');
    
    if (vendasEl) vendasEl.textContent = totalVendas;
    if (receitaEl) receitaEl.textContent = totalReceita;
}

/**
 * Configura botões de demonstração para tipos de relatórios
 */
function setupDemoButtons() {
    const demoButtons = document.querySelectorAll('.btn-relatorio-primary');
    
    demoButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Esta funcionalidade estará disponível em breve!');
        });
    });
} 