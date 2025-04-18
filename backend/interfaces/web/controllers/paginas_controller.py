"""
Blueprint para as rotas web de páginas do sistema.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Criar blueprint
paginas_bp = Blueprint('paginas', __name__)


# Middleware de autenticação
def requer_login(f):
    """Decorator para garantir que o usuário está logado"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("É necessário fazer login para acessar esta página", "warning")
            return redirect(url_for('paginas.login', proximo=request.path))
        return f(*args, **kwargs)

    return decorated_function


def requer_gerente(f):
    """Decorator para garantir que o usuário é um gerente ou dev"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("É necessário fazer login para acessar esta página", "warning")
            return redirect(url_for('paginas.login', proximo=request.path))
        if session.get('usuario_tipo') not in ['gerente', 'dev']:
            flash("Acesso negado. Esta página é restrita a gerentes.", "danger")
            return redirect(url_for('paginas.index'))
        return f(*args, **kwargs)

    return decorated_function


# Rotas
@paginas_bp.route('/')
def index():
    """Página inicial - catálogo de produtos"""
    return render_template("index.html")


@paginas_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    from backend.application.services.usuario_service import UsuarioService
    from backend.infrastructure.repositories.usuario_repository import UsuarioRepository

    # Instanciar serviço
    usuario_repository = UsuarioRepository()
    usuario_service = UsuarioService(usuario_repository)

    proximo = request.args.get('proximo', '/')

    if request.method == 'POST':
        credencial = request.form.get('credencial')
        senha = request.form.get('senha')

        if not credencial or not senha:
            flash("Por favor, informe suas credenciais", "danger")
            return render_template("login.html", proximo=proximo)

        try:
            # Autenticar usuário
            resultado = usuario_service.autenticar(credencial, senha)

            if resultado['sucesso']:
                # Salvar dados na sessão
                session['usuario_id'] = resultado['usuario']['id']
                session['usuario_nome'] = resultado['usuario']['nome']
                session['usuario_tipo'] = resultado['usuario']['tipo']

                flash(f"Bem-vindo(a), {resultado['usuario']['nome']}!", "success")
                return redirect(proximo)
            else:
                flash(resultado['mensagem'], "danger")
        except Exception as e:
            logger.error(f"Erro ao processar login: {str(e)}")
            flash("Erro ao processar login. Tente novamente.", "danger")

    return render_template("login.html", proximo=proximo)


@paginas_bp.route('/logout')
def logout():
    """Rota para logout do usuário"""
    session.clear()
    flash("Você saiu do sistema", "info")
    return redirect(url_for('paginas.index'))


@paginas_bp.route('/estoque')
@requer_login
def estoque():
    """Página de gerenciamento de estoque"""
    return render_template("estoque.html")


@paginas_bp.route('/lista_pedidos')
@requer_login
def lista_pedidos():
    """Página de listagem de pedidos"""
    from backend.application.services.pedido_service import PedidoService
    from backend.infrastructure.repositories.pedido_repository import PedidoRepository

    # Instanciar serviço
    pedido_repository = PedidoRepository()
    pedido_service = PedidoService(pedido_repository)

    try:
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


@paginas_bp.route('/listar_usuarios')
@requer_gerente
def listar_usuarios():
    """Página de gerenciamento de usuários"""
    return render_template("usuarios.html")


@paginas_bp.route('/relatorios')
@requer_login
def relatorios():
    """Página de relatórios"""
    return render_template("relatorios.html")