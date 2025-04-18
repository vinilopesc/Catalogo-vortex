@produtos_bp.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    """API para adicionar um novo produto"""
    try:
        # Extrair dados do formulário
        dados = {
            'nome': request.form.get('nome'),
            'descricao': request.form.get('descricao', ''),
            'preco': float(request.form.get('preco', 0)),
            'quantidade_estoque': int(request.form.get('quantidade_estoque', 0)),
        }
        
        # Processar upload de imagem
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{imagem.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Garantir que o diretório existe
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                imagem.save(filepath)
                dados['imagem_url'] = f"/static/images/produtos/{filename}"
        
        # Criar produto
        produto = produto_service.criar_produto(dados)
        
        return jsonify({
            "id": produto['id'],
            "mensagem": "Produto adicionado com sucesso"
        }), 201
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@produtos_bp.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    """API para atualizar um produto existente"""
    try:
        # Obter dados do corpo da requisição
        dados = request.json
        
        # Atualizar produto
        produto = produto_service.atualizar_produto(produto_id, dados)
        
        return jsonify({
            "mensagem": "Produto atualizado com sucesso",
            "produto": produto
        })
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao atualizar produto {produto_id}: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@produtos_bp.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def excluir_produto(produto_id):
    """API para excluir um produto"""
    try:
        # Excluir produto
        sucesso = produto_service.excluir_produto(produto_id)
        
        if sucesso:
            return jsonify({"mensagem": "Produto excluído com sucesso"})
        else:
            return jsonify({"erro": "Produto não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao excluir produto {produto_id}: {str(e)}")
        return jsonify({"erro": str(e)}), 500