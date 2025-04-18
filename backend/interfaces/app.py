"""
Módulo principal para criação e configuração da aplicação Flask.
"""

from flask import Flask, render_template, request, session
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Cria e configura a aplicação Flask.

    Returns:
        Flask: Aplicação Flask configurada
    """
    # Instanciar aplicação
    app = Flask(
        __name__,
        template_folder='../../frontend/templates',
        static_folder='../../frontend/static'
    )

    # Configurar app
    app.secret_key = os.getenv("APP_SECRET_KEY", "vortex")
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # Adicionar variáveis de contexto global para templates
    @app.context_processor
    def adicionar_variaveis_globais():
        """Adiciona variáveis de contexto global para todos os templates"""
        from datetime import datetime
        # Por padrão, sem notificações
        return {
            'notification_count': 0,
            'notifications': [],
            'current_year': datetime.now().year,
            'app_version': '1.0.0'
        }

    # Registrar blueprints
    from backend.interfaces.api.produtos_blueprint import produtos_bp
    from backend.interfaces.api.pedidos_blueprint import pedidos_bp
    from backend.interfaces.api.usuarios_blueprint import usuarios_bp
    from backend.interfaces.web.controllers.paginas_controller import paginas_bp

    app.register_blueprint(produtos_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(paginas_bp)

    # Configurar handlers de erro
    @app.errorhandler(404)
    def pagina_nao_encontrada(e):
        """Página de erro 404"""
        return render_template("404.html", url=request.path), 404

    @app.errorhandler(500)
    def erro_interno(e):
        """Página de erro 500"""
        return render_template("erro.html", mensagem="Ocorreu um erro interno no servidor."), 500

    # Garantir que os diretórios importantes existam
    os.makedirs('frontend/static/images/produtos', exist_ok=True)
    os.makedirs('frontend/static/css', exist_ok=True)
    os.makedirs('frontend/static/js', exist_ok=True)

    logger.info("Aplicação Flask configurada com sucesso")
    return app