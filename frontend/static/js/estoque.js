// Editar produto
function editarProdutoModal(id) {
    const produto = produtos.find(p => p.id == id);
    if (!produto) return;

    // Preencher formulário
    document.getElementById('editar-id').value = produto.id;
    document.getElementById('editar-nome').value = produto.nome;
    // Garantir que o preço seja tratado como número
    const preco = parseFloat(produto.preco) || 0;
    document.getElementById('editar-preco').value = `R$ ${preco.toFixed(2)}`.replace('.', ',');
    document.getElementById('editar-estoque').value = produto.quantidade_estoque;
    document.getElementById('editar-descricao').value = produto.descricao || '';

    // Imagem atual
    document.getElementById('editar-imagem-preview').src = produto.imagem_url || '/static/images/produtos/placeholder.jpg';

    // Fechar o modal de visualização se estiver aberto
    const visualizarModal = bootstrap.Modal.getInstance(document.getElementById('visualizarProdutoModal'));
    if (visualizarModal) {
        visualizarModal.hide();
    }

    // Abrir modal de edição
    const editarModal = new bootstrap.Modal(document.getElementById('editarProdutoModal'));
    editarModal.show();
}

// Salvar edição do produto
async function salvarEdicao() {
    // Obter os dados do formulário
    const id = document.getElementById('editar-id').value;
    const nome = document.getElementById('editar-nome').value;
    const precoFormatado = document.getElementById('editar-preco').value;
    const estoque = document.getElementById('editar-estoque').value;
    const descricao = document.getElementById('editar-descricao').value;

    // Validação básica
    if (!nome || !precoFormatado || estoque === undefined) {
        mostrarNotificacao('error', 'Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    // Extrair valor numérico do preço formatado
    const precoNumerico = extrairValorNumerico(precoFormatado);

    try {
        // Mostrar indicador de carregamento
        const btnSalvar = document.querySelector('#editarProdutoModal .modal-footer .btn-primary');
        const btnTextoOriginal = btnSalvar.innerHTML;
        btnSalvar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        btnSalvar.disabled = true;

        // Enviar requisição para a API
        const response = await fetch(`/api/produtos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nome: nome,
                preco: parseFloat(precoNumerico),
                quantidade_estoque: parseInt(estoque),
                descricao: descricao
            })
        });

        if (!response.ok) {
            throw new Error(`Erro ao atualizar produto: ${response.status}`);
        }

        // Recarregar produtos
        await carregarProdutos();

        // Mostrar notificação de sucesso
        mostrarNotificacao('success', 'Produto atualizado com sucesso!');

        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editarProdutoModal'));
        modal.hide();
    } catch (error) {
        console.error('Erro ao salvar produto:', error);
        mostrarNotificacao('error', `Erro ao salvar alterações: ${error.message}`);
    } finally {
        // Restaurar botão
        const btnSalvar = document.querySelector('#editarProdutoModal .modal-footer .btn-primary');
        btnSalvar.innerHTML = '<i class="bi bi-check-circle"></i> Salvar Alterações';
        btnSalvar.disabled = false;
    }
}

// Excluir produto (modal de confirmação)
function excluirProdutoModal(id, nome) {
    produtoParaExcluir = id;
    document.getElementById('produto-excluir-nome').textContent = nome;

    // Abrir modal de confirmação
    const modal = new bootstrap.Modal(document.getElementById('confirmarExclusaoModal'));
    modal.show();
}

// Confirmar exclusão
async function confirmarExclusao() {
    if (!produtoParaExcluir) return;

    try {
        // Mostrar indicador de carregamento
        const btnExcluir = document.querySelector('#confirmarExclusaoModal .btn-danger');
        const btnTextoOriginal = btnExcluir.innerHTML;
        btnExcluir.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Excluindo...';
        btnExcluir.disabled = true;

        // Enviar requisição para a API
        const response = await fetch(`/api/produtos/${produtoParaExcluir}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`Erro ao excluir produto: ${response.status}`);
        }

        // Recarregar produtos
        await carregarProdutos();

        // Mostrar notificação de sucesso
        mostrarNotificacao('success', 'Produto excluído com sucesso!');

        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmarExclusaoModal'));
        modal.hide();

    } catch (error) {
        console.error('Erro ao excluir produto:', error);
        mostrarNotificacao('error', `Erro ao excluir produto: ${error.message}`);
    } finally {
        // Restaurar botão
        const btnExcluir = document.querySelector('#confirmarExclusaoModal .btn-danger');
        btnExcluir.innerHTML = '<i class="bi bi-trash"></i> Excluir Produto';
        btnExcluir.disabled = false;

        // Limpar referência
        produtoParaExcluir = null;
    }
}

// Mostrar notificação toast
function mostrarNotificacao(tipo, mensagem) {
    // Configurações baseadas no tipo
    let icone, classe, titulo;

    switch (tipo) {
        case 'success':
            icone = 'bi-check-circle-fill';
            classe = 'bg-success';
            titulo = 'Sucesso';
            break;
        case 'warning':
            icone = 'bi-exclamation-triangle-fill';
            classe = 'bg-warning';
            titulo = 'Atenção';
            break;
        case 'error':
            icone = 'bi-exclamation-circle-fill';
            classe = 'bg-danger';
            titulo = 'Erro';
            break;
        default:
            icone = 'bi-info-circle-fill';
            classe = 'bg-info';
            titulo = 'Informação';
    }

    // Criar elemento toast
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="toast-header">
            <i class="bi ${icone} me-2 text-${tipo === 'success' ? 'success' : (tipo === 'warning' ? 'warning' : (tipo === 'error' ? 'danger' : 'info'))}"></i>
            <strong class="me-auto">${titulo}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>
        </div>
        <div class="toast-body">
            ${mensagem}
        </div>
    `;

    // Adicionar ao container
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        toastContainer.appendChild(toast);

        // Inicializar e mostrar
        const bsToast = new bootstrap.Toast(toast, {
            delay: 5000
        });
        bsToast.show();

        // Remover do DOM quando fechado
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

/**
 * JavaScript para a página de Estoque Redesenhada
 * Catálogo Vortex - Versão moderna com melhor UX
 */

// Variáveis globais
let produtos = [];
let produtoPaginaAtual = 1;
let produtosPorPagina = 9;
let produtoParaExcluir = null;
let visualizandoProdutoId = null;
let filtroAtivo = 'todos';
let ordenacaoAtiva = 'id-desc';

// Variáveis para movimentações
let movimentacoes = [];
let movimentacaoPaginaAtual = 1;
let movimentacoesPorPagina = 10;
let filtroMovimentacoes = 'todos';

// Ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Carregar produtos
    carregarProdutos();

    // Inicializar componentes
    inicializarEventos();

    // Configurar a aba de movimentações se ela existir
    if (document.getElementById('movimentacoes-tab')) {
        // Carregar lista de produtos para o select
        carregarProdutosSelect();
        
        // Carregar movimentações do estoque
        carregarMovimentacoes();
        
        // Configurar evento para registrar movimentação
        document.getElementById('btn-registrar-movimentacao').addEventListener('click', registrarMovimentacao);
        
        // Configurar filtro de movimentações
        document.getElementById('filtro-movimentacoes').addEventListener('change', function() {
            filtroMovimentacoes = this.value;
            movimentacaoPaginaAtual = 1;
            aplicarFiltrosMovimentacoes();
        });
        
        // Inicializar data com a data atual
        document.getElementById('data_movimentacao').valueAsDate = new Date();
    }
});

// Inicializar eventos
function inicializarEventos() {
    // Atualizar estatísticas quando mudar de aba
    document.getElementById('listar-tab').addEventListener('click', function() {
        setTimeout(atualizarEstatisticas, 100);
    });

    // Configurar preview de imagem
    const inputImagem = document.getElementById('imagem');
    if (inputImagem) {
        inputImagem.addEventListener('change', previewImagem);
    }

    // Selecionar a aba de cadastro se o parâmetro na URL for "cadastrar"
    if (window.location.search.includes('acao=cadastrar')) {
        const cadastrarTab = new bootstrap.Tab(document.getElementById('cadastrar-tab'));
        cadastrarTab.show();
    }

    // Selecionar botões de filtro
    const filtroBotoes = document.querySelectorAll('.filtro-btn');
    filtroBotoes.forEach(botao => {
        botao.addEventListener('click', function() {
            const filtro = this.getAttribute('data-filtro');

            // Atualizar estado ativo
            filtroBotoes.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            filtroAtivo = filtro;
            produtoPaginaAtual = 1;

            // Aplicar filtros
            aplicarFiltros();
        });
    });

    // Configurar ordenação
    document.getElementById('ordem-produtos').addEventListener('change', function() {
        ordenacaoAtiva = this.value;
        produtoPaginaAtual = 1;
        aplicarFiltros();
    });
}

// Carregar produtos da API
async function carregarProdutos() {
    try {
        const response = await fetch('/api/produtos');
        if (!response.ok) {
            throw new Error(`Erro ao carregar produtos: ${response.status}`);
        }

        // Obter os produtos e garantir que os tipos sejam corretos
        const produtosData = await response.json();
        
        // Normalizar os dados para garantir que os tipos sejam corretos
        produtos = produtosData.map(produto => ({
            ...produto,
            id: parseInt(produto.id) || 0,
            preco: parseFloat(produto.preco) || 0,
            quantidade_estoque: parseInt(produto.quantidade_estoque) || 0,
            descricao: produto.descricao || '',
            imagem_url: produto.imagem_url || null
        }));

        // Aplicar filtros e ordenação
        aplicarFiltros();

        // Atualizar estatísticas
        atualizarEstatisticas();

    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        document.getElementById('produtos-container').innerHTML = `
            <div class="alert alert-danger" style="grid-column: 1 / -1;">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Erro ao carregar produtos: ${error.message}
                <button class="btn btn-sm btn-outline-danger ms-3" onclick="carregarProdutos()">
                    <i class="bi bi-arrow-clockwise me-1"></i> Tentar novamente
                </button>
            </div>
        `;
    }
}

// Atualizar estatísticas
function atualizarEstatisticas() {
    if (!produtos || !produtos.length) return;

    // Total de produtos
    const totalProdutos = produtos.length;
    document.getElementById('total-produtos').textContent = totalProdutos;

    // Valor total em estoque
    const valorEstoque = produtos.reduce((total, produto) => {
        // Garantir que preco seja número
        const preco = parseFloat(produto.preco) || 0;
        return total + (preco * produto.quantidade_estoque);
    }, 0);
    document.getElementById('valor-estoque').textContent = `R$ ${valorEstoque.toFixed(2)}`;

    // Produtos com baixo estoque (menos de 5)
    const baixoEstoque = produtos.filter(produto => produto.quantidade_estoque > 0 && produto.quantidade_estoque <= 5).length;
    document.getElementById('produtos-baixo-estoque').textContent = baixoEstoque;
}

// Aplicar filtros e ordenação
function aplicarFiltros() {
    if (!produtos || !produtos.length) return;

    let produtosFiltrados = [...produtos];

    // Aplicar filtro de busca
    const termoBusca = document.getElementById('busca-produto').value.trim().toLowerCase();
    if (termoBusca) {
        // Preparar termos para busca por preço (substituir vírgula por ponto para comparação)
        const termoBuscaPreco = termoBusca.replace(',', '.');
        
        produtosFiltrados = produtosFiltrados.filter(produto => {
            // Verificar nome
            if (produto.nome.toLowerCase().includes(termoBusca)) {
                return true;
            }
            
            // Verificar descrição
            if (produto.descricao && produto.descricao.toLowerCase().includes(termoBusca)) {
                return true;
            }
            
            // Verificar ID
            if (produto.id.toString().includes(termoBusca)) {
                return true;
            }
            
            // Verificar preço - tanto formatado (com R$) quanto numérico
            const precoNumerico = parseFloat(produto.preco) || 0;
            const precoFormatado = precoNumerico.toFixed(2).toString();
            const precoComSimbolo = `r$ ${precoFormatado}`.replace('.', ',');
            
            return precoFormatado.includes(termoBuscaPreco) || 
                   precoComSimbolo.includes(termoBusca);
        });
    }

    // Aplicar filtro de categoria
    if (filtroAtivo === 'baixo-estoque') {
        produtosFiltrados = produtosFiltrados.filter(produto =>
            produto.quantidade_estoque > 0 && produto.quantidade_estoque <= 5
        );
    } else if (filtroAtivo === 'sem-estoque') {
        produtosFiltrados = produtosFiltrados.filter(produto =>
            produto.quantidade_estoque === 0
        );
    }

    // Aplicar ordenação
    switch (ordenacaoAtiva) {
        case 'nome-asc':
            produtosFiltrados.sort((a, b) => a.nome.localeCompare(b.nome));
            break;
        case 'nome-desc':
            produtosFiltrados.sort((a, b) => b.nome.localeCompare(a.nome));
            break;
        case 'preco-asc':
            produtosFiltrados.sort((a, b) => parseFloat(a.preco) - parseFloat(b.preco));
            break;
        case 'preco-desc':
            produtosFiltrados.sort((a, b) => parseFloat(b.preco) - parseFloat(a.preco));
            break;
        case 'estoque-asc':
            produtosFiltrados.sort((a, b) => parseInt(a.quantidade_estoque) - parseInt(b.quantidade_estoque));
            break;
        case 'estoque-desc':
            produtosFiltrados.sort((a, b) => parseInt(b.quantidade_estoque) - parseInt(a.quantidade_estoque));
            break;
        case 'id-desc':
        default:
            produtosFiltrados.sort((a, b) => parseInt(b.id) - parseInt(a.id));
            break;
    }

    renderizarProdutos(produtosFiltrados);
}

// Filtrar produtos (busca)
function filtrarProdutos() {
    aplicarFiltros();
}

// Filtrar por categoria (botões)
function filtrarPorCategoria(filtro) {
    filtroAtivo = filtro;
    produtoPaginaAtual = 1;
    aplicarFiltros();
}

// Renderizar produtos
function renderizarProdutos(produtosFiltrados) {
    const container = document.getElementById('produtos-container');

    // Se não houver produtos
    if (!produtosFiltrados || produtosFiltrados.length === 0) {
        container.innerHTML = `
            <div class="sem-produtos" style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem;">
                <i class="bi bi-search" style="font-size: 3rem; color: var(--gray); display: block; margin-bottom: 1rem;"></i>
                <h3>Nenhum produto encontrado</h3>
                <p class="text-muted">Tente mudar os filtros ou adicione um novo produto.</p>
                <button class="btn btn-primary mt-3" onclick="abrirAbaAdicionar()">
                    <i class="bi bi-plus-circle me-2"></i>Adicionar Novo Produto
                </button>
            </div>
        `;

        // Limpar paginação
        document.getElementById('paginacao').innerHTML = '';
        return;
    }

    // Calcular páginas para paginação
    const totalPaginas = Math.ceil(produtosFiltrados.length / produtosPorPagina);

    // Ajustar página atual se necessário
    if (produtoPaginaAtual > totalPaginas) {
        produtoPaginaAtual = totalPaginas;
    }

    // Obter produtos da página atual
    const inicio = (produtoPaginaAtual - 1) * produtosPorPagina;
    const fim = Math.min(inicio + produtosPorPagina, produtosFiltrados.length);
    const produtosPagina = produtosFiltrados.slice(inicio, fim);

    // Limpar container
    container.innerHTML = '';

    // Adicionar cards de produtos
    produtosPagina.forEach(produto => {
        // Definir badge de estoque
        let badgeEstoque = '';
        let badgeClass = '';

        if (produto.quantidade_estoque <= 0) {
            badgeEstoque = 'Sem estoque';
            badgeClass = 'badge-estoque-baixo';
        } else if (produto.quantidade_estoque <= 5) {
            badgeEstoque = `${produto.quantidade_estoque} un.`;
            badgeClass = 'badge-estoque-baixo';
        } else if (produto.quantidade_estoque <= 20) {
            badgeEstoque = `${produto.quantidade_estoque} un.`;
            badgeClass = 'badge-estoque-medio';
        } else {
            badgeEstoque = `${produto.quantidade_estoque} un.`;
            badgeClass = 'badge-estoque-alto';
        }

        // Garantir que o preço seja um número
        const preco = parseFloat(produto.preco) || 0;

        // Criar card de produto
        const card = document.createElement('div');
        card.className = 'produto-card';
        card.innerHTML = `
            <div class="produto-imagem-container">
                <img src="${produto.imagem_url || '/static/images/produtos/placeholder.jpg'}"
                     alt="${produto.nome}"
                     class="produto-image">
                <span class="produto-badge ${badgeClass}">${badgeEstoque}</span>
                <div class="produto-acoes">
                    <button class="produto-acao-btn btn-visualizar" onclick="visualizarProduto(${produto.id})" title="Visualizar">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="produto-acao-btn btn-editar" onclick="editarProdutoModal(${produto.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="produto-acao-btn btn-excluir" onclick="excluirProdutoModal(${produto.id}, '${produto.nome.replace(/'/g, "\\'")}')" title="Excluir">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="produto-info">
                <h3 class="produto-titulo">${produto.nome}</h3>
                <p class="produto-descricao">${produto.descricao || 'Sem descrição'}</p>
                <div class="produto-preco-container">
                    <div class="produto-preco">R$ ${preco.toFixed(2)}</div>
                    <div class="produto-quantidade">
                        <i class="bi bi-box-seam"></i> ${produto.quantidade_estoque}
                    </div>
                </div>
            </div>
        `;

        container.appendChild(card);
    });

    // Atualizar paginação
    atualizarPaginacao(totalPaginas, produtosFiltrados.length);
}

// Atualizar paginação
function atualizarPaginacao(totalPaginas, totalProdutos) {
    const paginacao = document.getElementById('paginacao');
    paginacao.innerHTML = '';

    if (totalPaginas <= 1) return;

    // Informação de produtos por página
    const inicio = ((produtoPaginaAtual - 1) * produtosPorPagina) + 1;
    const fim = Math.min(produtoPaginaAtual * produtosPorPagina, totalProdutos);

    // Botão anterior
    const btnAnterior = document.createElement('button');
    btnAnterior.className = `pagina-item ${produtoPaginaAtual === 1 ? 'disabled' : ''}`;
    btnAnterior.innerHTML = '<i class="bi bi-chevron-left"></i>';
    btnAnterior.disabled = produtoPaginaAtual === 1;
    btnAnterior.addEventListener('click', () => mudarPagina(produtoPaginaAtual - 1));
    paginacao.appendChild(btnAnterior);

    // Páginas
    const maxPaginas = 5; // Máximo de botões de página a mostrar
    let paginaInicial = Math.max(1, produtoPaginaAtual - Math.floor(maxPaginas / 2));
    let paginaFinal = Math.min(totalPaginas, paginaInicial + maxPaginas - 1);

    // Ajustar se necessário para sempre mostrar maxPaginas
    if (paginaFinal - paginaInicial + 1 < maxPaginas && paginaInicial > 1) {
        paginaInicial = Math.max(1, paginaFinal - maxPaginas + 1);
    }

    // Adicionar botão para a primeira página se necessário
    if (paginaInicial > 1) {
        const btnPrimeira = document.createElement('button');
        btnPrimeira.className = 'pagina-item';
        btnPrimeira.textContent = '1';
        btnPrimeira.addEventListener('click', () => mudarPagina(1));
        paginacao.appendChild(btnPrimeira);

        // Adicionar elipses se houver mais páginas entre a primeira e a inicial
        if (paginaInicial > 2) {
            const elipses = document.createElement('span');
            elipses.className = 'pagina-item disabled';
            elipses.textContent = '...';
            paginacao.appendChild(elipses);
        }
    }

    // Adicionar botões de página
    for (let i = paginaInicial; i <= paginaFinal; i++) {
        const btnPagina = document.createElement('button');
        btnPagina.className = `pagina-item ${i === produtoPaginaAtual ? 'active' : ''}`;
        btnPagina.textContent = i;
        btnPagina.addEventListener('click', () => mudarPagina(i));
        paginacao.appendChild(btnPagina);
    }

    // Adicionar elipses e última página se necessário
    if (paginaFinal < totalPaginas) {
        if (paginaFinal < totalPaginas - 1) {
            const elipses = document.createElement('span');
            elipses.className = 'pagina-item disabled';
            elipses.textContent = '...';
            paginacao.appendChild(elipses);
        }

        const btnUltima = document.createElement('button');
        btnUltima.className = 'pagina-item';
        btnUltima.textContent = totalPaginas;
        btnUltima.addEventListener('click', () => mudarPagina(totalPaginas));
        paginacao.appendChild(btnUltima);
    }

    // Botão próxima
    const btnProxima = document.createElement('button');
    btnProxima.className = `pagina-item ${produtoPaginaAtual === totalPaginas ? 'disabled' : ''}`;
    btnProxima.innerHTML = '<i class="bi bi-chevron-right"></i>';
    btnProxima.disabled = produtoPaginaAtual === totalPaginas;
    btnProxima.addEventListener('click', () => mudarPagina(produtoPaginaAtual + 1));
    paginacao.appendChild(btnProxima);
}

// Mudar página
function mudarPagina(pagina) {
    produtoPaginaAtual = pagina;
    aplicarFiltros();
    window.scrollTo({top: 0, behavior: 'smooth'});
}

// Preview de imagem
function previewImagem() {
    const inputImagem = document.getElementById('imagem');
    const previewWrapper = document.getElementById('imagem-preview-wrapper');
    const preview = document.getElementById('imagem-preview');

    if (inputImagem.files && inputImagem.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.src = e.target.result;
            previewWrapper.classList.add('com-imagem');
        }

        reader.readAsDataURL(inputImagem.files[0]);
    } else {
        preview.src = '/static/images/produtos/placeholder.jpg';
        previewWrapper.classList.remove('com-imagem');
    }
}

// Limpar preview
function limparPreview() {
    const preview = document.getElementById('imagem-preview');
    const previewWrapper = document.getElementById('imagem-preview-wrapper');

    preview.src = '/static/images/produtos/placeholder.jpg';
    previewWrapper.classList.remove('com-imagem');
}

// Abrir aba de adicionar produto
function abrirAbaAdicionar() {
    const cadastrarTab = new bootstrap.Tab(document.getElementById('cadastrar-tab'));
    cadastrarTab.show();
}

// Visualizar produto
function visualizarProduto(id) {
    const produto = produtos.find(p => p.id == id);
    if (!produto) return;

    // Armazenar ID do produto visualizado
    visualizandoProdutoId = id;

    // Preencher modal com informações do produto
    document.getElementById('visualizar-nome').textContent = produto.nome;
    // Garantir que o preço seja um número
    const preco = parseFloat(produto.preco) || 0;
    document.getElementById('visualizar-preco').textContent = preco.toFixed(2);
    document.getElementById('visualizar-id').textContent = produto.id;
    document.getElementById('visualizar-descricao').textContent = produto.descricao || 'Sem descrição disponível para este produto.';

    // Status de estoque
    const estoqueBadge = document.getElementById('visualizar-estoque-badge');
    if (produto.quantidade_estoque <= 0) {
        estoqueBadge.className = 'badge esgotado';
        estoqueBadge.innerHTML = 'Estoque: <span id="visualizar-estoque">Esgotado</span>';
    } else if (produto.quantidade_estoque <= 5) {
        estoqueBadge.className = 'badge baixo';
        estoqueBadge.innerHTML = `Estoque: <span id="visualizar-estoque">${produto.quantidade_estoque} un.</span>`;
    } else {
        estoqueBadge.className = 'badge';
        estoqueBadge.innerHTML = `Estoque: <span id="visualizar-estoque">${produto.quantidade_estoque} un.</span>`;
    }

    // Imagem
    document.getElementById('visualizar-imagem').src = produto.imagem_url || '/static/images/produtos/placeholder.jpg';

    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('visualizarProdutoModal'));
    modal.show();
}

// Funções de formatação monetária
function formatarMoeda(input) {
    // Remove todos os caracteres não numéricos
    let valor = input.value.replace(/\D/g, '');
    
    // Se não houver valor, retorna zero formatado
    if (!valor) {
        input.value = 'R$ 0,00';
        return;
    }
    
    // Converte para número e divide por 100 para ter os centavos
    valor = (parseInt(valor) / 100).toFixed(2);
    
    // Formata com símbolo R$ e separadores adequados
    valor = `R$ ${valor}`.replace('.', ',');
    
    // Atualiza o valor do campo
    input.value = valor;
}

function validarValorMonetario(input) {
    if (input.value.trim() === '' || input.value === 'R$ 0,00') {
        input.value = 'R$ 0,00';
        return;
    }
    
    // Garante que há um valor mínimo e uma formatação consistente
    formatarMoeda(input);
}

function extrairValorNumerico(valorFormatado) {
    // Remove o símbolo R$, espaços e converte vírgula para ponto
    return valorFormatado.replace('R$', '').replace(/\s/g, '').replace(',', '.');
}

// Inicializar campos monetários quando o documento carregar
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar eventos para campos monetários existentes
    const camposMonetarios = document.querySelectorAll('input[data-tipo="moeda"]');
    camposMonetarios.forEach(campo => {
        campo.addEventListener('keyup', function() { formatarMoeda(this); });
        campo.addEventListener('blur', function() { validarValorMonetario(this); });
        
        // Inicializar com R$ 0,00
        if (!campo.value) {
            campo.value = 'R$ 0,00';
        }
    });
});

// Carregar produtos para o select de movimentações
async function carregarProdutosSelect() {
    if (!produtos || !produtos.length) {
        // Se os produtos ainda não foram carregados, espere um pouco e tente novamente
        setTimeout(carregarProdutosSelect, 500);
        return;
    }

    const select = document.getElementById('produto_id');
    select.innerHTML = '<option value="" selected disabled>Selecione um produto</option>';

    // Ordenar por nome para facilitar a seleção
    const produtosOrdenados = [...produtos].sort((a, b) => a.nome.localeCompare(b.nome));

    produtosOrdenados.forEach(produto => {
        const option = document.createElement('option');
        option.value = produto.id;
        option.textContent = `${produto.nome} (${produto.quantidade_estoque} em estoque)`;
        select.appendChild(option);
    });
}

// Carregar movimentações do estoque
async function carregarMovimentacoes() {
    try {
        const response = await fetch('/api/estoque/movimentacoes');
        if (!response.ok) {
            throw new Error(`Erro ao carregar movimentações: ${response.status}`);
        }

        // Obter os dados e normalizar
        const movimentacoesData = await response.json();
        
        // Normalizar os dados
        movimentacoes = movimentacoesData.map(mov => ({
            ...mov,
            id: parseInt(mov.id) || 0,
            produto_id: parseInt(mov.produto_id) || 0,
            quantidade: parseInt(mov.quantidade) || 0,
            preco_unitario: parseFloat(mov.preco_unitario) || 0,
            estoque_anterior: parseInt(mov.estoque_anterior) || 0,
            estoque_atual: parseInt(mov.estoque_atual) || 0,
            data: new Date(mov.data),
            produto_nome: mov.produto_nome || 'Produto não encontrado'
        }));

        // Aplicar filtros
        aplicarFiltrosMovimentacoes();

    } catch (error) {
        console.error('Erro ao carregar movimentações:', error);
        document.getElementById('tabela-movimentacoes-body').innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-3 text-danger">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Erro ao carregar movimentações: ${error.message}
                    <button class="btn btn-sm btn-outline-danger ms-3" onclick="carregarMovimentacoes()">
                        <i class="bi bi-arrow-clockwise me-1"></i> Tentar novamente
                    </button>
                </td>
            </tr>
        `;
    }
}

// Aplicar filtros às movimentações
function aplicarFiltrosMovimentacoes() {
    if (!movimentacoes || !movimentacoes.length) {
        document.getElementById('tabela-movimentacoes-body').innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-3 text-muted">
                    <i class="bi bi-inbox me-2"></i>
                    Nenhuma movimentação registrada
                </td>
            </tr>
        `;
        return;
    }

    // Filtrar por tipo
    let movimentacoesFiltradas = [...movimentacoes];
    if (filtroMovimentacoes !== 'todos') {
        movimentacoesFiltradas = movimentacoesFiltradas.filter(mov => mov.tipo === filtroMovimentacoes);
    }

    // Ordenar por data (mais recentes primeiro)
    movimentacoesFiltradas.sort((a, b) => b.data - a.data);

    // Paginação
    const totalPaginas = Math.ceil(movimentacoesFiltradas.length / movimentacoesPorPagina);
    
    // Ajustar página atual se necessário
    if (movimentacaoPaginaAtual > totalPaginas) {
        movimentacaoPaginaAtual = totalPaginas || 1;
    }

    // Obter movimentações da página atual
    const inicio = (movimentacaoPaginaAtual - 1) * movimentacoesPorPagina;
    const fim = Math.min(inicio + movimentacoesPorPagina, movimentacoesFiltradas.length);
    const movimentacoesPagina = movimentacoesFiltradas.slice(inicio, fim);

    renderizarMovimentacoes(movimentacoesPagina);
    atualizarPaginacaoMovimentacoes(totalPaginas, movimentacoesFiltradas.length);
}

// Renderizar movimentações na tabela
function renderizarMovimentacoes(movimentacoesPagina) {
    const tbody = document.getElementById('tabela-movimentacoes-body');

    if (!movimentacoesPagina || !movimentacoesPagina.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-3 text-muted">
                    <i class="bi bi-funnel me-2"></i>
                    Nenhuma movimentação encontrada com os filtros atuais
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';

    movimentacoesPagina.forEach(mov => {
        const tr = document.createElement('tr');
        tr.className = 'cursor-pointer';
        tr.onclick = () => visualizarMovimentacao(mov.id);
        
        // Formatar data
        const data = mov.data;
        const dataFormatada = `${data.getDate().toString().padStart(2, '0')}/${(data.getMonth() + 1).toString().padStart(2, '0')}/${data.getFullYear()}`;
        
        // Calcular valor total
        const valorTotal = mov.quantidade * mov.preco_unitario;

        // Tipo de movimentação (com classe CSS para cor)
        const tipoClasse = mov.tipo === 'entrada' ? 'bg-success' : 'bg-danger';
        const tipoTexto = mov.tipo === 'entrada' ? 'Entrada' : 'Saída';

        tr.innerHTML = `
            <td>${dataFormatada}</td>
            <td>${mov.produto_nome}</td>
            <td><span class="badge ${tipoClasse}">${tipoTexto}</span></td>
            <td>${mov.quantidade} un.</td>
            <td>R$ ${mov.preco_unitario.toFixed(2)}</td>
            <td class="fw-bold">R$ ${valorTotal.toFixed(2)}</td>
        `;

        tbody.appendChild(tr);
    });
}

// Atualizar paginação de movimentações
function atualizarPaginacaoMovimentacoes(totalPaginas, totalMovimentacoes) {
    const paginacao = document.getElementById('paginacao-movimentacoes');
    paginacao.innerHTML = '';

    if (totalPaginas <= 1) return;

    // Informação de movimentações por página
    const inicio = ((movimentacaoPaginaAtual - 1) * movimentacoesPorPagina) + 1;
    const fim = Math.min(movimentacaoPaginaAtual * movimentacoesPorPagina, totalMovimentacoes);

    // Botão anterior
    const btnAnterior = document.createElement('button');
    btnAnterior.className = `pagina-item ${movimentacaoPaginaAtual === 1 ? 'disabled' : ''}`;
    btnAnterior.innerHTML = '<i class="bi bi-chevron-left"></i>';
    btnAnterior.disabled = movimentacaoPaginaAtual === 1;
    btnAnterior.addEventListener('click', () => mudarPaginaMovimentacoes(movimentacaoPaginaAtual - 1));
    paginacao.appendChild(btnAnterior);

    // Adicionar páginas (simplificado para economizar espaço)
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === 1 || i === totalPaginas || (i >= movimentacaoPaginaAtual - 1 && i <= movimentacaoPaginaAtual + 1)) {
            const btnPagina = document.createElement('button');
            btnPagina.className = `pagina-item ${i === movimentacaoPaginaAtual ? 'active' : ''}`;
            btnPagina.textContent = i;
            btnPagina.addEventListener('click', () => mudarPaginaMovimentacoes(i));
            paginacao.appendChild(btnPagina);
        } else if (i === movimentacaoPaginaAtual - 2 || i === movimentacaoPaginaAtual + 2) {
            const elipses = document.createElement('span');
            elipses.className = 'pagina-item disabled';
            elipses.textContent = '...';
            paginacao.appendChild(elipses);
        }
    }

    // Botão próxima
    const btnProxima = document.createElement('button');
    btnProxima.className = `pagina-item ${movimentacaoPaginaAtual === totalPaginas ? 'disabled' : ''}`;
    btnProxima.innerHTML = '<i class="bi bi-chevron-right"></i>';
    btnProxima.disabled = movimentacaoPaginaAtual === totalPaginas;
    btnProxima.addEventListener('click', () => mudarPaginaMovimentacoes(movimentacaoPaginaAtual + 1));
    paginacao.appendChild(btnProxima);
}

// Mudar página de movimentações
function mudarPaginaMovimentacoes(pagina) {
    movimentacaoPaginaAtual = pagina;
    aplicarFiltrosMovimentacoes();
}

// Registrar nova movimentação
async function registrarMovimentacao() {
    // Validar formulário
    const form = document.getElementById('form-movimentacao');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Obter dados do formulário
    const produtoId = document.getElementById('produto_id').value;
    const tipoMovimentacao = document.getElementById('tipo_movimentacao').value;
    const quantidade = parseInt(document.getElementById('quantidade').value);
    const precoUnitarioFormatado = document.getElementById('preco_unitario').value;
    const precoUnitario = extrairValorNumerico(precoUnitarioFormatado);
    const dataMovimentacao = document.getElementById('data_movimentacao').value;
    const observacao = document.getElementById('observacao').value;

    // Validar quantidade
    if (quantidade <= 0) {
        mostrarNotificacao('error', 'A quantidade deve ser maior que zero.');
        return;
    }

    // Verificar se é uma saída e se há estoque suficiente
    if (tipoMovimentacao === 'saida') {
        const produto = produtos.find(p => p.id == produtoId);
        if (!produto) {
            mostrarNotificacao('error', 'Produto não encontrado.');
            return;
        }

        if (quantidade > produto.quantidade_estoque) {
            mostrarNotificacao('warning', `Estoque insuficiente. Disponível: ${produto.quantidade_estoque} unidades.`);
            return;
        }
    }

    try {
        // Mostrar indicador de carregamento
        const btn = document.getElementById('btn-registrar-movimentacao');
        const btnTexto = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registrando...';
        btn.disabled = true;

        // Preparar dados para envio
        const dados = {
            produto_id: parseInt(produtoId),
            tipo: tipoMovimentacao,
            quantidade: quantidade,
            preco_unitario: parseFloat(precoUnitario),
            data: dataMovimentacao,
            observacao: observacao
        };

        // Enviar para a API
        const response = await fetch('/api/estoque/movimentacoes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.erro || `Erro ao registrar movimentação: ${response.status}`);
        }

        const result = await response.json();

        // Exibir mensagem de sucesso
        mostrarNotificacao('success', 'Movimentação registrada com sucesso!');

        // Limpar formulário
        form.reset();
        document.getElementById('data_movimentacao').valueAsDate = new Date();

        // Recarregar movimentações e produtos
        await Promise.all([carregarMovimentacoes(), carregarProdutos()]);

    } catch (error) {
        console.error('Erro ao registrar movimentação:', error);
        mostrarNotificacao('error', error.message);
    } finally {
        // Restaurar botão
        const btn = document.getElementById('btn-registrar-movimentacao');
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Registrar Movimentação';
        btn.disabled = false;
    }
}

// Visualizar detalhes da movimentação
function visualizarMovimentacao(id) {
    const movimentacao = movimentacoes.find(m => m.id == id);
    if (!movimentacao) return;

    // Formatar data
    const data = movimentacao.data;
    const dataFormatada = `${data.getDate().toString().padStart(2, '0')}/${(data.getMonth() + 1).toString().padStart(2, '0')}/${data.getFullYear()}`;
    const horaFormatada = `${data.getHours().toString().padStart(2, '0')}:${data.getMinutes().toString().padStart(2, '0')}`;

    // Calcular valor total
    const valorTotal = movimentacao.quantidade * movimentacao.preco_unitario;

    // Preencher modal
    document.getElementById('detalhes-produto').textContent = movimentacao.produto_nome;
    
    // Tipo da movimentação
    const tipoElement = document.getElementById('detalhes-tipo-badge');
    if (movimentacao.tipo === 'entrada') {
        tipoElement.className = 'badge bg-success';
        tipoElement.textContent = 'Entrada (Compra)';
    } else {
        tipoElement.className = 'badge bg-danger';
        tipoElement.textContent = 'Saída (Retirada)';
    }

    document.getElementById('detalhes-data').textContent = `${dataFormatada} às ${horaFormatada}`;
    document.getElementById('detalhes-quantidade').textContent = `${movimentacao.quantidade} unidades`;
    document.getElementById('detalhes-valor-unitario').textContent = `R$ ${movimentacao.preco_unitario.toFixed(2)}`;
    document.getElementById('detalhes-valor-total').textContent = `R$ ${valorTotal.toFixed(2)}`;
    document.getElementById('detalhes-observacao').textContent = movimentacao.observacao || 'Nenhuma observação registrada.';
    document.getElementById('detalhes-estoque-anterior').textContent = `${movimentacao.estoque_anterior} unidades`;
    document.getElementById('detalhes-estoque-atual').textContent = `${movimentacao.estoque_atual} unidades`;

    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('detalhesMovimentacaoModal'));
    modal.show();
}

// Exportar estoque para Excel
function exportarEstoqueExcel() {
    // Mostrar indicador de carregamento
    mostrarNotificacao('info', 'Gerando arquivo Excel, aguarde...');
    
    // Fazer a requisição para a API
    fetch('/api/estoque/exportar-excel', {
        method: 'GET',
        headers: {
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao gerar o arquivo Excel');
        }
        return response.blob();
    })
    .then(blob => {
        // Criar URL para o blob
        const url = window.URL.createObjectURL(blob);
        
        // Criar elemento de link temporário para download
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Gerar nome do arquivo com data atual
        const date = new Date();
        const timestamp = date.toISOString().split('T')[0].replace(/-/g, '');
        a.download = `estoque_${timestamp}.xlsx`;
        
        // Adicionar ao documento, clicar e remover
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Notificar sucesso
        mostrarNotificacao('success', 'Relatório de estoque gerado com sucesso!');
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarNotificacao('error', 'Erro ao gerar o relatório: ' + error.message);
    });
}