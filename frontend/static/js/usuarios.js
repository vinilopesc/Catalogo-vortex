/**
 * Funcionalidades específicas para a página de usuários
 * Catálogo Vortex
 */

let usuarios = [];
let usuarioIdAtual = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarUsuarios();
    
    // Adicionar event listeners para filtros
    document.getElementById('busca-usuario').addEventListener('input', aplicarFiltros);
    document.getElementById('filtro-tipo').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-status').addEventListener('change', aplicarFiltros);
});

/**
 * Alterna a visibilidade da senha entre texto e asteriscos
 */
function toggleSenha(id) {
    const input = document.getElementById(id);
    const icon = event.currentTarget.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

/**
 * Carrega a lista de usuários da API
 */
async function carregarUsuarios() {
    try {
        const response = await fetch('/api/usuarios');
        if (!response.ok) {
            throw new Error('Erro ao carregar usuários');
        }
        usuarios = await response.json();
        exibirUsuarios(usuarios);
        atualizarEstatisticas();
    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('usuarios-tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="alert alert-danger mb-0">
                        Erro ao carregar usuários. Por favor, tente novamente.
                    </div>
                </td>
            </tr>
        `;
    }
}

/**
 * Atualiza os cards de estatísticas com números atualizados
 */
function atualizarEstatisticas() {
    const totalUsuarios = usuarios.length;
    const totalGerentes = usuarios.filter(u => u.tipo === 'gerente').length;
    const totalVendedores = usuarios.filter(u => u.tipo === 'vendedor').length;
    const totalClientes = usuarios.filter(u => u.tipo === 'cliente').length;
    
    document.getElementById('total-usuarios').textContent = totalUsuarios;
    document.getElementById('total-gerentes').textContent = totalGerentes;
    document.getElementById('total-vendedores').textContent = totalVendedores;
    document.getElementById('total-clientes').textContent = totalClientes;
}

/**
 * Exibe os usuários na tabela
 */
function exibirUsuarios(usuariosFiltrados) {
    const tbody = document.getElementById('usuarios-tbody');
    
    if (usuariosFiltrados.length === 0) {
        document.getElementById('sem-resultados').classList.remove('d-none');
        tbody.innerHTML = '';
        return;
    }
    
    document.getElementById('sem-resultados').classList.add('d-none');
    
    let html = '';
    usuariosFiltrados.forEach((usuario, index) => {
        html += `
            <tr>
                <td>${usuario.id}</td>
                <td>
                    <div class="usuario-info">
                        <div class="avatar-container">
                            ${usuario.foto ? `<img src="${usuario.foto}" alt="${usuario.nome}">` : '<i class="bi bi-person avatar-placeholder"></i>'}
                        </div>
                        <div class="usuario-details">
                            <h6>${usuario.nome}</h6>
                            <p>Cadastrado em ${new Date(usuario.data_cadastro).toLocaleDateString()}</p>
                        </div>
                    </div>
                </td>
                <td>${usuario.email}</td>
                <td><span class="usuario-tipo ${usuario.tipo}">${usuario.tipo.charAt(0).toUpperCase() + usuario.tipo.slice(1)}</span></td>
                <td><span class="usuario-status ${usuario.status}">${usuario.status.charAt(0).toUpperCase() + usuario.status.slice(1)}</span></td>
                <td>
                    <div class="usuario-actions">
                        <button class="btn-icon" onclick="prepararEdicao(${usuario.id})" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn-icon" onclick="prepararExclusao(${usuario.id}, '${usuario.nome}')" title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

/**
 * Aplica filtros na lista de usuários
 */
function aplicarFiltros() {
    const busca = document.getElementById('busca-usuario').value.toLowerCase();
    const tipo = document.getElementById('filtro-tipo').value;
    const status = document.getElementById('filtro-status').value;
    
    let usuariosFiltrados = usuarios.filter(usuario => {
        const match = (
            usuario.nome.toLowerCase().includes(busca) ||
            usuario.email.toLowerCase().includes(busca) ||
            usuario.id.toString().includes(busca)
        );
        
        const matchTipo = tipo ? usuario.tipo === tipo : true;
        const matchStatus = status ? usuario.status === status : true;
        
        return match && matchTipo && matchStatus;
    });
    
    exibirUsuarios(usuariosFiltrados);
}

/**
 * Prepara o modal para edição de um usuário
 */
function prepararEdicao(id) {
    const usuario = usuarios.find(u => u.id === id);
    if (!usuario) return;
    
    usuarioIdAtual = id;
    document.getElementById('editar-id').value = usuario.id;
    document.getElementById('editar-nome').value = usuario.nome;
    document.getElementById('editar-email').value = usuario.email;
    document.getElementById('editar-senha').value = '';
    document.getElementById('editar-tipo').value = usuario.tipo;
    document.getElementById('editar-status').value = usuario.status;
    
    const modal = new bootstrap.Modal(document.getElementById('editarUsuarioModal'));
    modal.show();
}

/**
 * Prepara o modal para confirmar exclusão de um usuário
 */
function prepararExclusao(id, nome) {
    usuarioIdAtual = id;
    document.getElementById('nome-usuario-exclusao').textContent = nome;
    
    document.getElementById('btn-confirmar-exclusao').onclick = function() {
        excluirUsuario(id);
    };
    
    const modal = new bootstrap.Modal(document.getElementById('confirmacaoExclusaoModal'));
    modal.show();
}

/**
 * Adiciona um novo usuário
 */
async function adicionarUsuario() {
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const tipo = document.getElementById('tipo').value;
    
    if (!nome || !email || !senha || !tipo) {
        alert('Por favor, preencha todos os campos obrigatórios.');
        return;
    }
    
    try {
        const response = await fetch('/api/usuarios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nome,
                email,
                senha,
                tipo,
                status: 'ativo'
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao adicionar usuário');
        }
        
        const novoUsuario = await response.json();
        
        // Adicionar o novo usuário à lista
        usuarios.push(novoUsuario);
        
        // Atualizar a tabela e estatísticas
        exibirUsuarios(usuarios);
        atualizarEstatisticas();
        
        // Limpar o formulário e fechar o modal
        document.getElementById('form-adicionar-usuario').reset();
        bootstrap.Modal.getInstance(document.getElementById('adicionarUsuarioModal')).hide();
        
        // Exibir mensagem de sucesso
        mostrarToast('Usuário adicionado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('Erro ao adicionar usuário. Por favor, tente novamente.', 'danger');
    }
}

/**
 * Atualiza um usuário existente
 */
async function atualizarUsuario() {
    const id = document.getElementById('editar-id').value;
    const nome = document.getElementById('editar-nome').value;
    const email = document.getElementById('editar-email').value;
    const senha = document.getElementById('editar-senha').value;
    const tipo = document.getElementById('editar-tipo').value;
    const status = document.getElementById('editar-status').value;
    
    if (!nome || !email || !tipo || !status) {
        mostrarToast('Por favor, preencha todos os campos obrigatórios.', 'warning');
        return;
    }
    
    const dadosAtualizacao = {
        nome,
        email,
        tipo,
        status
    };
    
    // Adicionar senha apenas se foi informada
    if (senha) {
        dadosAtualizacao.senha = senha;
    }
    
    try {
        const response = await fetch(`/api/usuarios/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosAtualizacao)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao atualizar usuário');
        }
        
        const usuarioAtualizado = await response.json();
        
        // Atualizar o usuário na lista
        const index = usuarios.findIndex(u => u.id === parseInt(id));
        if (index !== -1) {
            usuarios[index] = usuarioAtualizado;
        }
        
        // Atualizar a tabela e estatísticas
        exibirUsuarios(usuarios);
        atualizarEstatisticas();
        
        // Fechar o modal
        bootstrap.Modal.getInstance(document.getElementById('editarUsuarioModal')).hide();
        
        // Exibir mensagem de sucesso
        mostrarToast('Usuário atualizado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('Erro ao atualizar usuário. Por favor, tente novamente.', 'danger');
    }
}

/**
 * Exclui um usuário
 */
async function excluirUsuario(id) {
    try {
        const response = await fetch(`/api/usuarios/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erro ao excluir usuário');
        }
        
        // Remover o usuário da lista
        usuarios = usuarios.filter(u => u.id !== id);
        
        // Atualizar a tabela e estatísticas
        exibirUsuarios(usuarios);
        atualizarEstatisticas();
        
        // Fechar o modal
        bootstrap.Modal.getInstance(document.getElementById('confirmacaoExclusaoModal')).hide();
        
        // Exibir mensagem de sucesso
        mostrarToast('Usuário excluído com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('Erro ao excluir usuário. Por favor, tente novamente.', 'danger');
    }
}

/**
 * Exibe uma mensagem toast
 */
function mostrarToast(mensagem, tipo = 'info') {
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${tipo} border-0`;
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
    
    document.querySelector('.toast-container').appendChild(toastEl);
    
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