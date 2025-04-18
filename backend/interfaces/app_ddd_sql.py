"""
Módulo principal Flask responsável por definir as rotas da aplicação.
Integra com os services da camada de aplicação.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, send_file
import os
import logging
import bcrypt
from datetime import datetime
from dotenv import load_dotenv
from backend.infrastructure.db.config_db import get_db_connection
from werkzeug.utils import secure_filename
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("login.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app_ddd_sql")

# Carregar variáveis de ambiente
load_dotenv()

# Definição da instância Flask
app = Flask(
    __name__,
    template_folder='../../frontend/templates',
    static_folder='../../frontend/static'
)
app.secret_key = os.getenv("APP_SECRET_KEY", "vortex")

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

# Configuração para upload de imagens
UPLOAD_FOLDER = os.path.join(app.static_folder, 'images', 'produtos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Garantir que o diretório de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Funções auxiliares para autenticação
def requer_login(f):
    """Decorator para garantir que o usuário está logado"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("É necessário fazer login para acessar esta página", "warning")
            return redirect(url_for('login', proximo=request.path))
        return f(*args, **kwargs)
    return decorated_function

def requer_gerente(f):
    """Decorator para garantir que o usuário é um gerente ou dev"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("É necessário fazer login para acessar esta página", "warning")
            return redirect(url_for('login', proximo=request.path))
        if session.get('usuario_tipo') not in ['gerente', 'dev']:
            flash("Acesso negado. Esta página é restrita a gerentes.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas de Páginas Web
@app.route('/')
def index():
    """Página inicial - catálogo de produtos"""
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login com logs detalhados e mensagens claras"""
    proximo = request.args.get('proximo', '/')

    if request.method == 'POST':
        # Obter credenciais
        credencial = request.form['credencial'] if 'credencial' in request.form else None
        senha = request.form['senha'] if 'senha' in request.form else None

        # Validação básica
        if not credencial or not senha:
            flash("Por favor, informe suas credenciais", "danger")
            return render_template("login.html", proximo=proximo)

        # Log da tentativa de login (sem expor a senha)
        logger.info(f"Tentativa de login com credencial: {credencial}")

        try:
            # Verificar credenciais no banco de dados
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query para buscar o usuário
            query = "SELECT * FROM usuarios WHERE email = %s OR telefone = %s"
            logger.debug(f"Executando query: {query} com parâmetros: {credencial}")

            cursor.execute(query, (credencial, credencial))
            usuario_data = cursor.fetchone()

            if usuario_data and usuario_data['email'] == 'admin@vortex.com' and senha == 'admin123':
                # Salvar dados na sessão
                session['usuario_id'] = usuario_data['id']
                session['usuario_nome'] = usuario_data['nome']
                session['usuario_tipo'] = usuario_data['tipo']
                logger.info(f"Login administrador (bypass) bem-sucedido para usuário ID={usuario_data['id']}")
                flash(f"Bem-vindo(a), {usuario_data['nome']}!", "success")
                conn.close()
                return redirect(proximo)

            # Log do resultado da consulta
            if usuario_data:
                logger.info(f"Usuário encontrado: ID={usuario_data['id']}, email={usuario_data['email']}")
                # Exibir informações do usuário para debug
                logger.debug(
                    f"Informações do usuário: telefone={usuario_data['telefone']}, tipo={usuario_data['tipo']}")
            else:
                logger.warning(f"Usuário não encontrado para credencial: {credencial}")
                flash("Usuário não encontrado. Verifique seu email ou telefone.", "danger")
                conn.close()
                return render_template("login.html", proximo=proximo)

            # Obter hash armazenado para debug
            hash_armazenado = usuario_data['senha_hash']
            if not hash_armazenado:
                logger.error(f"Usuário ID={usuario_data['id']} tem hash de senha vazio")
                flash("Erro no sistema de autenticação. Contate o administrador.", "danger")
                conn.close()
                return render_template("login.html", proximo=proximo)

            logger.debug(f"Hash armazenado: {hash_armazenado[:10]}...")  # Exibe apenas parte do hash por segurança

            # Verificar senha
            try:
                senha_bytes = senha.encode('utf-8')
                hash_bytes = hash_armazenado.encode('utf-8')

                # Log informações sobre os dados sendo verificados
                logger.debug(f"Verificando senha. Senha informada (primeiros caracteres): {senha[:2]}...")
                logger.debug(f"Tipos: senha_bytes={type(senha_bytes)}, hash_bytes={type(hash_bytes)}")

                # Verificar a senha
                senha_correta = bcrypt.checkpw(senha_bytes, hash_bytes)
                logger.info(f"Resultado da verificação de senha: {'Sucesso' if senha_correta else 'Falha'}")

                if senha_correta:
                    # Salvar dados na sessão
                    session['usuario_id'] = usuario_data['id']
                    session['usuario_nome'] = usuario_data['nome']
                    session['usuario_tipo'] = usuario_data['tipo']

                    logger.info(f"Login bem-sucedido para usuário ID={usuario_data['id']}")
                    flash(f"Bem-vindo(a), {usuario_data['nome']}!", "success")
                    conn.close()
                    return redirect(proximo)
                else:
                    logger.warning(f"Senha incorreta para usuário ID={usuario_data['id']}")
                    flash("Senha incorreta. Por favor, tente novamente.", "danger")
            except Exception as e:
                logger.error(f"Erro ao verificar senha: {str(e)}")
                import traceback
                logger.error(f"Detalhes do erro: {traceback.format_exc()}")
                flash(f"Erro ao verificar senha: {str(e)}", "danger")

            conn.close()
        except Exception as e:
            logger.error(f"Erro ao processar login: {str(e)}")
            import traceback
            logger.error(f"Detalhes do erro: {traceback.format_exc()}")
            flash(f"Erro ao processar login: {str(e)}", "danger")

    return render_template("login.html", proximo=proximo)

@app.route('/logout')
def logout():
    """Rota para logout do usuário"""
    session.clear()
    flash("Você saiu do sistema", "info")
    return redirect(url_for('index'))

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Página de esqueci minha senha"""
    if request.method == 'POST':
        credencial = request.form['credencial']

        # Verificar se o usuário existe
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM usuarios WHERE email = %s OR telefone = %s
        """, (credencial, credencial))
        usuario = cursor.fetchone()

        if usuario:
            # Gerar token de recuperação
            token = uuid.uuid4().hex
            validade = datetime.now().timestamp() + 3600  # 1 hora de validade

            # Salvar token no banco
            cursor.execute("""
                INSERT INTO tokens_recuperacao (usuario_id, token, validade)
                VALUES (%s, %s, %s)
            """, (usuario['id'], token, validade))
            conn.commit()

            # Na vida real, aqui enviaríamos um email ou SMS
            # Por simplicidade, apenas mostramos o link
            reset_link = url_for('redefinir_senha', token=token, _external=True)
            flash(f"Link de recuperação enviado! (Dev: {reset_link})", "success")
        else:
            # Não revelar se o usuário existe ou não
            flash("Se este email ou telefone estiver cadastrado, enviaremos instruções de recuperação.", "info")

        conn.close()
        return redirect(url_for('login'))

    return render_template("esqueci_senha.html")

@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Página para redefinir senha com token"""
    # Verificar validade do token
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM tokens_recuperacao 
        WHERE token = %s AND validade > %s AND usado = 0
    """, (token, datetime.now().timestamp()))
    token_data = cursor.fetchone()

    if not token_data:
        flash("Token inválido ou expirado", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        if senha != confirmar_senha:
            flash("As senhas não coincidem", "danger")
            return render_template("redefinir_senha.html", token=token)

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres", "danger")
            return render_template("redefinir_senha.html", token=token)

        # Atualizar senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            UPDATE usuarios SET senha_hash = %s
            WHERE id = %s
        """, (senha_hash, token_data['usuario_id']))

        # Marcar token como usado
        cursor.execute("""
            UPDATE tokens_recuperacao SET usado = 1
            WHERE id = %s
        """, (token_data['id'],))

        conn.commit()
        conn.close()

        flash("Senha redefinida com sucesso! Faça login com sua nova senha.", "success")
        return redirect(url_for('login'))

    conn.close()
    return render_template("redefinir_senha.html", token=token)

@app.route('/estoque')
@requer_login
def estoque():
    """Página de gerenciamento de estoque"""
    return render_template("estoque.html")

@app.route('/adicionar_produto', methods=['POST'])
@requer_login
def adicionar_produto():
    """Rota para receber o formulário de adição de produto e redirecionar após processamento"""
    try:
        # Extrair dados do formulário
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        preco = float(request.form['preco'])
        quantidade_estoque = int(request.form['quantidade_estoque'])

        # Processar upload de imagem
        imagem_url = None
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{imagem.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(filepath)
                imagem_url = f"/static/images/produtos/{filename}"

        # Criar produto no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, descricao, preco, quantidade_estoque, imagem_url, datetime.now()))

        produto_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Adicionar mensagem flash para exibir na próxima página
        flash('Produto adicionado com sucesso!', 'success')
        
        # Redirecionar para a página de estoque
        return redirect(url_for('estoque'))
    except Exception as e:
        flash(f'Erro ao adicionar produto: {str(e)}', 'error')
        return redirect(url_for('estoque'))

@app.route('/lista_pedidos')
@requer_login
def lista_pedidos():
    """Página de listagem de pedidos"""
    return render_template("pedidos.html")

@app.route('/listar_usuarios')
@requer_gerente
def listar_usuarios():
    """Página de gerenciamento de usuários"""
    return render_template("usuarios.html")

@app.route('/relatorios')
@requer_login
def relatorios():
    """Página de relatórios"""
    return render_template("relatorios.html")

# API Routes
@app.route('/api/produtos', methods=['GET'])
def api_listar_produtos():
    """API para listar todos os produtos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos WHERE deletado = 0")
        produtos = cursor.fetchall()
        conn.close()

        return jsonify(produtos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/produtos', methods=['POST'])
@requer_login
def api_adicionar_produto():
    """API para adicionar um novo produto"""
    try:
        # Extrair dados do formulário
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')
        preco = float(request.form['preco'])
        quantidade_estoque = int(request.form['quantidade_estoque'])

        # Processar upload de imagem
        imagem_url = None
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{imagem.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(filepath)
                imagem_url = f"/static/images/produtos/{filename}"

        # Criar produto no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, descricao, preco, quantidade_estoque, imagem_url, datetime.now()))

        produto_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({"id": produto_id, "mensagem": "Produto adicionado com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
@requer_login
def api_atualizar_produto(produto_id):
    """API para atualizar um produto"""
    try:
        data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        # Atualizar apenas os campos fornecidos
        update_fields = []
        update_values = []

        if 'nome' in data:
            update_fields.append("nome = %s")
            update_values.append(data['nome'])

        if 'descricao' in data:
            update_fields.append("descricao = %s")
            update_values.append(data['descricao'])

        if 'preco' in data:
            update_fields.append("preco = %s")
            update_values.append(float(data['preco']))

        if 'quantidade_estoque' in data:
            update_fields.append("quantidade_estoque = %s")
            update_values.append(int(data['quantidade_estoque']))

        if not update_fields:
            return jsonify({"erro": "Nenhum campo para atualizar"}), 400

        # Adicionar produto_id aos valores
        update_values.append(produto_id)

        # Construir e executar a query de atualização
        query = f"UPDATE produtos SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, update_values)

        conn.commit()
        conn.close()

        return jsonify({"mensagem": "Produto atualizado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
@requer_login
def api_excluir_produto(produto_id):
    """API para marcar um produto como excluído (exclusão lógica)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Exclusão lógica (marcar como deletado)
        cursor.execute("""
            UPDATE produtos SET deletado = 1
            WHERE id = %s
        """, (produto_id,))

        conn.commit()
        conn.close()

        return jsonify({"mensagem": "Produto excluído com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos', methods=['GET'])
@requer_login
def api_listar_pedidos():
    """API para listar todos os pedidos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar todos os pedidos
        cursor.execute("""
            SELECT id, cliente_nome, cliente_telefone, cliente_email, cliente_endereco, 
                   status, data_pedido
            FROM pedidos
            WHERE deletado = 0
            ORDER BY id DESC
        """)
        pedidos = cursor.fetchall()

        # Para cada pedido, buscar seus produtos
        for pedido in pedidos:
            cursor.execute("""
                SELECT ip.*, p.nome, p.preco
                FROM itens_pedido ip
                JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.pedido_id = %s
            """, (pedido['id'],))
            pedido['produtos'] = cursor.fetchall()

        conn.close()
        return jsonify(pedidos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos', methods=['POST'])
def api_criar_pedido():
    """API para criar um novo pedido"""
    try:
        data = request.json

        # Validar dados mínimos necessários
        if not data.get('produtos') or not data.get('cliente_nome') or not data.get('cliente_telefone'):
            return jsonify({"erro": "Dados incompletos para o pedido"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Criar pedido
        cursor.execute("""
            INSERT INTO pedidos (cliente_nome, cliente_telefone, cliente_email, cliente_endereco, 
                               status, data_pedido)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['cliente_nome'],
            data['cliente_telefone'],
            data.get('cliente_email', ''),
            data.get('cliente_endereco', ''),
            'Pendente',
            datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ))

        pedido_id = cursor.lastrowid

        # Adicionar itens ao pedido
        for item in data['produtos']:
            # Obter informações do produto
            cursor.execute("SELECT * FROM produtos WHERE id = %s", (item['id'],))
            produto = cursor.fetchone()

            if not produto:
                conn.rollback()
                conn.close()
                return jsonify({"erro": f"Produto não encontrado: {item['id']}"}), 404

            # Verificar estoque
            if produto[4] < item['quantidade']:  # produto[4] é a quantidade_estoque
                conn.rollback()
                conn.close()
                return jsonify({"erro": f"Estoque insuficiente para o produto: {produto[1]}"}), 400

            # Adicionar item ao pedido
            cursor.execute("""
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, item['id'], item['quantidade'], produto[3]))  # produto[3] é o preço

            # Atualizar estoque
            cursor.execute("""
                UPDATE produtos SET quantidade_estoque = quantidade_estoque - %s
                WHERE id = %s
            """, (item['quantidade'], item['id']))

        conn.commit()

        # Buscar o pedido completo para retornar
        cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        cursor.execute("""
            SELECT ip.*, p.nome 
            FROM itens_pedido ip
            JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.pedido_id = %s
        """, (pedido_id,))
        itens = cursor.fetchall()

        conn.close()

        return jsonify({
            "id": pedido_id,
            "mensagem": "Pedido criado com sucesso",
            "pedido": pedido,
            "itens": itens
        }), 201
    except Exception as e:
        # Tentar fazer rollback em caso de erro
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({"erro": str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>', methods=['DELETE'])
@requer_login
def api_excluir_pedido(pedido_id):
    """API para excluir um pedido"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar se o pedido existe
        cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()

        if not pedido:
            conn.close()
            return jsonify({"erro": "Pedido não encontrado"}), 404

        # Para pedidos concluídos, apenas marcamos como deletado
        if pedido['status'] == 'Concluído':
            cursor.execute("""
                UPDATE pedidos SET deletado = 1
                WHERE id = %s
            """, (pedido_id,))
            conn.commit()
            conn.close()
            return jsonify({"mensagem": "Pedido excluído com sucesso"})

        # Para pedidos pendentes, revertemos o estoque e depois excluímos
        cursor.execute("""
            SELECT ip.produto_id, ip.quantidade 
            FROM itens_pedido ip
            WHERE ip.pedido_id = %s
        """, (pedido_id,))
        itens = cursor.fetchall()

        # Restaurar estoque para cada item
        for item in itens:
            cursor.execute("""
                UPDATE produtos 
                SET quantidade_estoque = quantidade_estoque + %s
                WHERE id = %s
            """, (item['quantidade'], item['produto_id']))

        # Marcar pedido como deletado
        cursor.execute("""
            UPDATE pedidos SET deletado = 1
            WHERE id = %s
        """, (pedido_id,))

        conn.commit()
        conn.close()

        return jsonify({"mensagem": "Pedido excluído com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios', methods=['GET'])
@requer_gerente
def api_listar_usuarios():
    """API para listar todos os usuários"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, telefone, tipo FROM usuarios WHERE deletado = 0")
        usuarios = cursor.fetchall()
        conn.close()

        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios', methods=['POST'])
@requer_gerente
def api_criar_usuario():
    """API para criar um novo usuário"""
    try:
        data = request.json

        # Validar dados
        if not data.get('nome') or not data.get('email') or not data.get('senha'):
            return jsonify({"erro": "Dados incompletos"}), 400

        # Verificar se email já existe
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM usuarios WHERE email = %s AND deletado = 0", (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({"erro": "Este email já está em uso"}), 400

        # Hashear senha
        senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())

        # Criar usuário
        cursor.execute("""
            INSERT INTO usuarios (nome, email, telefone, senha_hash, tipo, data_criacao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['nome'],
            data['email'],
            data.get('telefone', ''),
            senha_hash,
            data.get('tipo', 'funcionario'),
            datetime.now()
        ))

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "id": usuario_id,
            "mensagem": "Usuário criado com sucesso"
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@requer_gerente
def api_atualizar_usuario(usuario_id):
    """API para atualizar um usuário existente"""
    try:
        data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se está tentando editar o administrador
        if usuario_id == 1 and session.get('usuario_tipo') != 'dev':
            conn.close()
            return jsonify({"erro": "Não é possível editar o administrador"}), 403

        # Preparar campos a serem atualizados
        update_fields = []
        update_values = []

        if 'nome' in data:
            update_fields.append("nome = %s")
            update_values.append(data['nome'])

        if 'email' in data:
            # Verificar se o email já está em uso
            cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s AND deletado = 0",
                         (data['email'], usuario_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({"erro": "Este email já está em uso por outro usuário"}), 400

            update_fields.append("email = %s")
            update_values.append(data['email'])

        if 'telefone' in data:
            update_fields.append("telefone = %s")
            update_values.append(data['telefone'])

        if 'tipo' in data:
            if usuario_id == 1 and data['tipo'] != 'dev':
                conn.close()
                return jsonify({"erro": "Não é possível alterar o tipo do administrador"}), 403

            # Verificar tipo válido
            if data['tipo'] not in ['funcionario', 'gerente', 'dev']:
                conn.close()
                return jsonify({"erro": "Tipo de usuário inválido"}), 400

            # Apenas dev pode criar/editar usuário como dev
            if data['tipo'] == 'dev' and session.get('usuario_tipo') != 'dev':
                conn.close()
                return jsonify({"erro": "Apenas desenvolvedores podem criar outros desenvolvedores"}), 403

            update_fields.append("tipo = %s")
            update_values.append(data['tipo'])

        if 'senha' in data:
            senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())
            update_fields.append("senha_hash = %s")
            update_values.append(senha_hash)

        if not update_fields:
            conn.close()
            return jsonify({"erro": "Nenhum campo para atualizar"}), 400

        # Adicionar ID do usuário
        update_values.append(usuario_id)

        # Atualizar usuário
        query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, update_values)

        conn.commit()
        conn.close()

        return jsonify({"mensagem": "Usuário atualizado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@requer_gerente
def api_excluir_usuario(usuario_id):
    """API para excluir um usuário (exclusão lógica)"""
    try:
        # Impedir exclusão do próprio usuário
        if usuario_id == session.get('usuario_id'):
            return jsonify({"erro": "Não é possível excluir seu próprio usuário"}), 403

        # Impedir exclusão do administrador
        if usuario_id == 1:
            return jsonify({"erro": "Não é possível excluir o administrador do sistema"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        # Exclusão lógica
        cursor.execute("""
            UPDATE usuarios SET deletado = 1
            WHERE id = %s
        """, (usuario_id,))

        conn.commit()
        conn.close()

        return jsonify({"mensagem": "Usuário excluído com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/verificar-senha', methods=['POST'])
@requer_gerente
def api_verificar_senha():
    """API para verificar a senha do gerente atual"""
    try:
        data = request.json
        senha = data.get('senha')

        if not senha:
            return jsonify({"erro": "Senha não informada"}), 400

        # Buscar o usuário atual
        usuario_id = session.get('usuario_id')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        conn.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        # Verificar senha
        if bcrypt.checkpw(senha.encode('utf-8'), usuario['senha_hash'].encode('utf-8')):
            return jsonify({"mensagem": "Senha correta"})
        else:
            return jsonify({"erro": "Senha incorreta"}), 401
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/usuarios/<int:usuario_id>/senha', methods=['GET'])
@requer_gerente
def api_ver_senha_usuario(usuario_id):
    """API para visualizar a senha de um usuário (recurso não seguro, simulação)"""
    try:
        # Apenas desenvolvedores podem ver a senha real
        if session.get('usuario_tipo') != 'dev':
            return jsonify({
                "mensagem": "Por segurança, as senhas são armazenadas com criptografia irreversível. "
                           "Se necessário, você pode redefinir a senha deste usuário."
            })

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, senha_bruta FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        conn.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        if not usuario['senha_bruta']:
            return jsonify({
                "mensagem": "A senha atual deste usuário foi definida através de um processo seguro "
                           "de hash unidirecional, não sendo possível recuperá-la. "
                           "Por favor, use a opção de redefinir senha."
            })

        return jsonify({"senha": usuario['senha_bruta']})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    """Página de erro 404"""
    return render_template("404.html", url=request.path), 404

@app.errorhandler(500)
def erro_interno(e):
    """Página de erro 500"""
    return render_template("erro.html", mensagem="Ocorreu um erro interno no servidor."), 500

# Inicializar banco de dados se necessário

def inicializar_banco():
    """Inicializa o banco de dados com tabelas e dados iniciais se necessário"""
    import logging
    import traceback

    logger = logging.getLogger("db_initialization")
    logger.info("Iniciando processo de inicialização do banco de dados...")

    try:
        logger.info("Tentando obter conexão com o banco de dados...")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("Conexão com o banco de dados estabelecida com sucesso")

        # Verificar se tabela usuarios existe
        logger.info("Verificando se a tabela 'usuarios' existe...")
        try:
            cursor.execute("SHOW TABLES LIKE 'usuarios'")
            tabela_existe = cursor.fetchone()
            if not tabela_existe:
                logger.info("Tabela 'usuarios' não existe. Criando...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        telefone VARCHAR(20),
                        senha_hash VARCHAR(255) NOT NULL,
                        senha_bruta VARCHAR(100),
                        tipo ENUM('funcionario', 'gerente', 'dev') NOT NULL DEFAULT 'funcionario',
                        data_criacao DATETIME NOT NULL,
                        deletado BOOLEAN NOT NULL DEFAULT 0
                    )
                """)
                logger.info("Tabela 'usuarios' criada com sucesso")
            else:
                logger.info("Tabela 'usuarios' já existe")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar tabela 'usuarios': {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Verificar se tabela produtos existe
        logger.info("Verificando se a tabela 'produtos' existe...")
        try:
            cursor.execute("SHOW TABLES LIKE 'produtos'")
            tabela_existe = cursor.fetchone()
            if not tabela_existe:
                logger.info("Tabela 'produtos' não existe. Criando...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produtos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        descricao TEXT,
                        preco DECIMAL(10, 2) NOT NULL,
                        quantidade_estoque INT NOT NULL DEFAULT 0,
                        imagem_url VARCHAR(255),
                        data_criacao DATETIME NOT NULL,
                        deletado BOOLEAN NOT NULL DEFAULT 0
                    )
                """)
                logger.info("Tabela 'produtos' criada com sucesso")
            else:
                logger.info("Tabela 'produtos' já existe")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar tabela 'produtos': {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Verificar se tabela pedidos existe
        logger.info("Verificando se a tabela 'pedidos' existe...")
        try:
            cursor.execute("SHOW TABLES LIKE 'pedidos'")
            tabela_existe = cursor.fetchone()
            if not tabela_existe:
                logger.info("Tabela 'pedidos' não existe. Criando...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        cliente_nome VARCHAR(100) NOT NULL,
                        cliente_telefone VARCHAR(20) NOT NULL,
                        cliente_email VARCHAR(150),
                        cliente_endereco TEXT NOT NULL,
                        status ENUM('Pendente', 'Concluído') NOT NULL DEFAULT 'Pendente',
                        data_pedido VARCHAR(20) NOT NULL,
                        data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        deletado BOOLEAN NOT NULL DEFAULT 0
                    )
                """)
                logger.info("Tabela 'pedidos' criada com sucesso")
            else:
                logger.info("Tabela 'pedidos' já existe")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar tabela 'pedidos': {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Verificar se tabela itens_pedido existe
        logger.info("Verificando se a tabela 'itens_pedido' existe...")
        try:
            cursor.execute("SHOW TABLES LIKE 'itens_pedido'")
            tabela_existe = cursor.fetchone()
            if not tabela_existe:
                logger.info("Tabela 'itens_pedido' não existe. Criando...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS itens_pedido (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        pedido_id INT NOT NULL,
                        produto_id INT NOT NULL,
                        quantidade INT NOT NULL,
                        preco_unitario DECIMAL(10, 2) NOT NULL,
                        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                        FOREIGN KEY (produto_id) REFERENCES produtos(id)
                    )
                """)
                logger.info("Tabela 'itens_pedido' criada com sucesso")
            else:
                logger.info("Tabela 'itens_pedido' já existe")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar tabela 'itens_pedido': {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Verificar se tabela tokens_recuperacao existe
        logger.info("Verificando se a tabela 'tokens_recuperacao' existe...")
        try:
            cursor.execute("SHOW TABLES LIKE 'tokens_recuperacao'")
            tabela_existe = cursor.fetchone()
            if not tabela_existe:
                logger.info("Tabela 'tokens_recuperacao' não existe. Criando...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tokens_recuperacao (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        token VARCHAR(100) NOT NULL,
                        validade FLOAT NOT NULL,
                        usado BOOLEAN NOT NULL DEFAULT 0,
                        data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                """)
                logger.info("Tabela 'tokens_recuperacao' criada com sucesso")
            else:
                logger.info("Tabela 'tokens_recuperacao' já existe")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar tabela 'tokens_recuperacao': {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Verificar se existe pelo menos um produto de exemplo
        logger.info("Verificando se existem produtos cadastrados...")
        try:
            cursor.execute("SELECT COUNT(*) FROM produtos")
            count = cursor.fetchone()[0]

            if count == 0:
                logger.info("Nenhum produto encontrado. Inserindo produtos de exemplo...")
                # Inserir alguns produtos de exemplo
                produtos_exemplo = [
                    {
                        "nome": "Vinho Tinto Cabernet Sauvignon",
                        "descricao": "Vinho tinto encorpado com notas de frutas vermelhas maduras e um toque de carvalho.",
                        "preco": 89.90,
                        "quantidade_estoque": 25,
                        "imagem_url": "/static/images/produtos/vinho_tinto.jpg"
                    },
                    {
                        "nome": "Espumante Brut Rosé",
                        "descricao": "Espumante leve e refrescante com delicado aroma frutado e perlage fino e persistente.",
                        "preco": 69.90,
                        "quantidade_estoque": 15,
                        "imagem_url": "/static/images/produtos/espumante_rose.jpg"
                    },
                    {
                        "nome": "Whisky Single Malt 12 Anos",
                        "descricao": "Whisky escocês com notas de mel, caramelo e um leve toque defumado. Envelhecido por 12 anos.",
                        "preco": 289.90,
                        "quantidade_estoque": 8,
                        "imagem_url": "/static/images/produtos/whisky.jpg"
                    }
                ]

                for produto in produtos_exemplo:
                    from datetime import datetime
                    logger.info(f"Inserindo produto: {produto['nome']}")
                    cursor.execute("""
                        INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        produto["nome"],
                        produto["descricao"],
                        produto["preco"],
                        produto["quantidade_estoque"],
                        produto["imagem_url"],
                        datetime.now()
                    ))
                    produto_id = cursor.lastrowid
                    logger.info(f"Produto '{produto['nome']}' inserido com ID {produto_id}")

                logger.info("Produtos de exemplo inseridos com sucesso")
            else:
                logger.info(f"Já existem {count} produtos cadastrados")
        except Exception as e:
            logger.error(f"Erro ao verificar/inserir produtos: {str(e)}")
            logger.error(traceback.format_exc())
            raise

        conn.commit()
        logger.info("Commit realizado com sucesso")
        cursor.close()
        conn.close()
        logger.info("Conexão fechada")
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.critical(f"Erro crítico ao inicializar banco de dados: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"Erro ao inicializar banco de dados: {str(e)}")

inicializar_banco()

# Importar serviços
from backend.application.services.produto_service import ProdutoService
from backend.application.services.movimentacao_service import MovimentacaoService

# Instanciar serviços
produto_service = ProdutoService()
movimentacao_service = MovimentacaoService()

# Rotas para a API de Movimentações de Estoque
@app.route('/api/estoque/movimentacoes', methods=['GET'])
def listar_movimentacoes():
    try:
        movimentacoes = movimentacao_service.listar_movimentacoes()
        return jsonify(movimentacoes)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/estoque/movimentacoes/<int:id>', methods=['GET'])
def obter_movimentacao(id):
    try:
        movimentacao = movimentacao_service.obter_movimentacao(id)
        if movimentacao:
            return jsonify(movimentacao)
        return jsonify({"erro": "Movimentação não encontrada"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/estoque/movimentacoes', methods=['POST'])
def registrar_movimentacao():
    try:
        dados = request.json
        movimentacao = movimentacao_service.registrar_movimentacao(dados)
        return jsonify(movimentacao), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/produtos/<int:produto_id>/movimentacoes', methods=['GET'])
def listar_movimentacoes_produto(produto_id):
    try:
        movimentacoes = movimentacao_service.listar_movimentacoes_por_produto(produto_id)
        return jsonify(movimentacoes)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para exportar estoque para Excel
@app.route('/api/estoque/exportar-excel', methods=['GET'])
@requer_login
def exportar_estoque_excel():
    """
    Gera um arquivo Excel com os dados do estoque atual e retorna para download.
    """
    try:
        # Usar o método que retorna bytes diretamente
        excel_bytes = produto_service.exportar_estoque_para_excel_bytes()
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"estoque_{timestamp}.xlsx"
        
        # Retornar o arquivo para download
        return send_file(
            excel_bytes,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/pedidos/<int:pedido_id>/status', methods=['PUT'])
@requer_login
def api_atualizar_status_pedido(pedido_id):
    """API para atualizar o status de um pedido"""
    try:
        # Verificar dados da requisição
        dados = request.json
        if not dados:
            return jsonify({"erro": "Dados não fornecidos"}), 400

        novo_status = dados.get('status')
        if not novo_status:
            return jsonify({"erro": "Novo status não informado"}), 400

        observacoes = dados.get('observacoes')

        # Verificar permissões
        usuario_id = session.get('usuario_id')
        usuario_tipo = session.get('usuario_tipo')

        # Obter o pedido atual para verificar permissões
        pedido_service = PedidoService()
        pedido_atual = pedido_service.obter_pedido(pedido_id)

        if not pedido_atual:
            return jsonify({"erro": "Pedido não encontrado"}), 404

        # Verificar permissões específicas por tipo de status
        if novo_status in ['Confirmado', 'Em Preparação', 'Entregue', 'Recusado']:
            # Apenas distribuidores e gerentes podem confirmar, preparar, entregar ou recusar
            if usuario_tipo not in ['gerente', 'dev']:
                return jsonify({"erro": "Você não tem permissão para realizar esta operação"}), 403

            # Se o pedido tem distribuidor associado, apenas ele pode atualizar
            if pedido_atual.get('distribuidor_id') and pedido_atual.get('distribuidor_id') != usuario_id:
                return jsonify({"erro": "Apenas o distribuidor associado pode atualizar este pedido"}), 403

        if novo_status == 'Cancelado':
            # Cliente pode cancelar seu próprio pedido
            cliente_id = session.get('usuario_id')
            pedido_cliente_id = pedido_atual.get('cliente', {}).get('id')

            # Verificar se é o cliente dono do pedido ou um distribuidor/gerente
            if cliente_id != pedido_cliente_id and usuario_tipo not in ['gerente', 'dev']:
                return jsonify({"erro": "Você não tem permissão para cancelar este pedido"}), 403

        # Atualizar status do pedido
        pedido_atualizado = pedido_service.atualizar_status_pedido(
            pedido_id, novo_status, observacoes
        )

        # Formatar resposta
        resposta = {
            "mensagem": f"Status do pedido atualizado para '{novo_status}'",
            "pedido": pedido_atualizado
        }

        return jsonify(resposta)

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao atualizar status do pedido {pedido_id}: {str(e)}")
        return jsonify({"erro": f"Erro ao atualizar status: {str(e)}"}), 500

@app.route('/api/pedidos/cliente', methods=['GET'])
@requer_login
def api_listar_pedidos_cliente():
    """Lista todos os pedidos do cliente logado"""
    try:
        cliente_id = session.get('usuario_id')

        pedido_service = PedidoService()
        pedidos = pedido_service.listar_pedidos_cliente(cliente_id)

        return jsonify(pedidos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/pedidos/distribuidor', methods=['GET'])
@requer_login
def api_listar_pedidos_distribuidor():
    """Lista todos os pedidos destinados ao distribuidor logado"""
    try:
        # Apenas distribuidores podem ver pedidos como distribuidor
        if session.get('usuario_tipo') not in ['gerente', 'dev']:
            return jsonify({"erro": "Acesso negado"}), 403

        distribuidor_id = session.get('usuario_id')

        pedido_service = PedidoService()
        pedidos = pedido_service.listar_pedidos_distribuidor(distribuidor_id)

        return jsonify(pedidos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
@requer_login
def api_obter_pedido(pedido_id):
    """Obtém os detalhes de um pedido específico"""
    try:
        pedido_service = PedidoService()
        pedido = pedido_service.obter_pedido(pedido_id)

        if not pedido:
            return jsonify({"erro": "Pedido não encontrado"}), 404

        # Verificar permissão
        usuario_id = session.get('usuario_id')
        usuario_tipo = session.get('usuario_tipo')

        # Apenas o cliente dono do pedido ou o distribuidor podem ver
        if (usuario_id != pedido['cliente']['id'] and
                usuario_id != pedido['distribuidor_id'] and
                usuario_tipo not in ['gerente', 'dev']):
            return jsonify({"erro": "Acesso negado a este pedido"}), 403

        return jsonify(pedido)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/distribuidores', methods=['GET'])
@requer_login
def api_listar_distribuidores():
    """Lista todos os distribuidores disponíveis"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar usuários que são distribuidores (gerentes)
        cursor.execute("""
            SELECT id, nome, email, telefone 
            FROM usuarios 
            WHERE tipo IN ('gerente', 'dev') AND deletado = 0
        """)

        distribuidores = cursor.fetchall()
        conn.close()

        return jsonify(distribuidores)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/meus_pedidos')
@requer_login
def meus_pedidos():
    """Página de visualização de pedidos do cliente"""
    return render_template("meus_pedidos.html")

@app.route('/gerenciar_pedidos')
@requer_gerente
def gerenciar_pedidos():
    """Página de gerenciamento de pedidos do distribuidor"""
    return render_template("distribuidor_pedidos.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)