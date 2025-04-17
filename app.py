"""
Ponto de entrada principal da aplicação.

Inicializa o app Flask importando a instância do módulo app_ddd_sql.
"""

import sys
from pathlib import Path
import os
import logging

# Adicionar o diretório raiz ao path do Python
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Verificar diretórios importantes
os.makedirs('frontend/static/images/produtos', exist_ok=True)
os.makedirs('frontend/static/css', exist_ok=True)
os.makedirs('frontend/static/js', exist_ok=True)

# Importar o gerenciador de banco de dados e configurar o schema
logger.info("Verificando estrutura do banco de dados...")
from backend.infrastructure.db_manager import setup_database

if not setup_database():
    logger.error("Falha na inicialização do banco de dados. A aplicação pode não funcionar corretamente.")
else:
    logger.info("Banco de dados verificado e pronto!")

# Importar a instância da aplicação - CORRIGIDO
from backend.interfaces.app_ddd_sql import app  # Caminho correto

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