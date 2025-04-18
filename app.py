#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação Catálogo Vortex.
Inicializa o banco de dados, configura as dependências e inicia o servidor Flask.
"""

import sys
from pathlib import Path
import os
import logging
from datetime import datetime

# Adicionar o diretório raiz ao path do Python
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# Configurar o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

# Verificar diretórios importantes
os.makedirs('frontend/static/images/produtos', exist_ok=True)
os.makedirs('frontend/static/css', exist_ok=True)
os.makedirs('frontend/static/js', exist_ok=True)

# Verificar estrutura do banco de dados
logger.info("Verificando estrutura do banco de dados...")
from backend.infrastructure.db.db_manager import setup_database

if not setup_database():
    logger.error("Falha na inicialização do banco de dados. A aplicação pode não funcionar corretamente.")
else:
    logger.info("Banco de dados verificado e pronto!")

# Configurar injeção de dependências
logger.info("Configurando injeção de dependências...")

from backend.infrastructure.dependency_injection.container import Container
from backend.infrastructure.repositories.produto_repository import ProdutoRepository
from backend.infrastructure.repositories.pedido_repository import PedidoRepository
from backend.infrastructure.repositories.usuario_repository import UsuarioRepository
from backend.infrastructure.repositories.movimentacao_repository import MovimentacaoRepository
from backend.application.services.produto_service import ProdutoService
from backend.application.services.pedido_service import PedidoService
from backend.application.services.usuario_service import UsuarioService
from backend.application.services.movimentacao_service import MovimentacaoService
from backend.application.services.notificacao_service import NotificacaoService

# Registrar repositórios
produto_repository = ProdutoRepository()
Container.register('produto_repository', produto_repository)

pedido_repository = PedidoRepository()
Container.register('pedido_repository', pedido_repository)

usuario_repository = UsuarioRepository()
Container.register('usuario_repository', usuario_repository)

movimentacao_repository = MovimentacaoRepository()
Container.register('movimentacao_repository', movimentacao_repository)

# Registrar serviços
produto_service = ProdutoService(produto_repository)
Container.register('produto_service', produto_service)

pedido_service = PedidoService(pedido_repository, produto_repository)
Container.register('pedido_service', pedido_service)

usuario_service = UsuarioService(usuario_repository)
Container.register('usuario_service', usuario_service)

movimentacao_service = MovimentacaoService(movimentacao_repository, produto_repository)
Container.register('movimentacao_service', movimentacao_service)

notificacao_service = NotificacaoService()
Container.register('notificacao_service', notificacao_service)

logger.info("Injeção de dependências configurada com sucesso")

# Criar e iniciar a aplicação Flask
from backend.interfaces.app import create_app

app = create_app()

if __name__ == '__main__':
    # Obter porta da variável de ambiente ou usar 5000 como padrão
    port = int(os.environ.get('PORT', 5000))

    # Configurar modo de depuração baseado em variável de ambiente
    debug_mode = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"Iniciando aplicação Catálogo Vortex na porta {port}...")
    logger.info(f"Modo de depuração: {'ATIVADO' if debug_mode else 'DESATIVADO'}")
    logger.info(f"Acesse a aplicação em http://localhost:{port}/")

    # Iniciar o servidor
    app.run(host='0.0.0.0', port=port, debug=debug_mode)