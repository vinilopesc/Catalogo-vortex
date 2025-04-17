-- Script para inicialização do banco de dados do Catálogo Vortex
-- Criar banco de dados se não existir
CREATE DATABASE IF NOT EXISTS catalogo_vortex;
USE catalogo_vortex;

-- Tabela de usuários
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
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    imagem_url VARCHAR(255),
    data_criacao DATETIME NOT NULL,
    deletado BOOLEAN NOT NULL DEFAULT 0
);

-- Tabela de pedidos
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
);

-- Tabela de itens de pedido
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- Tabela de tokens de recuperação de senha
CREATE TABLE IF NOT EXISTS tokens_recuperacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token VARCHAR(100) NOT NULL,
    validade FLOAT NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT 0,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Inserindo alguns produtos de exemplo
INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Vinho Tinto Cabernet Sauvignon',
       'Vinho tinto encorpado com notas de frutas vermelhas maduras e um toque de carvalho.',
       89.90, 25, '/static/images/produtos/vinho_tinto.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Vinho Tinto Cabernet Sauvignon'
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Espumante Brut Rosé',
       'Espumante leve e refrescante com delicado aroma frutado e perlage fino e persistente.',
       69.90, 15, '/static/images/produtos/espumante_rose.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Espumante Brut Rosé'
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Whisky Single Malt 12 Anos',
       'Whisky escocês com notas de mel, caramelo e um leve toque defumado. Envelhecido por 12 anos.',
       289.90, 8, '/static/images/produtos/whisky.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Whisky Single Malt 12 Anos'
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Gin Premium London Dry',
       'Gin artesanal com botânicos selecionados, perfeito para drinks sofisticados.',
       129.90, 12, '/static/images/produtos/gin.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Gin Premium London Dry'
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Cerveja IPA Artesanal',
       'Cerveja India Pale Ale com notas cítricas e amargor acentuado. Produção artesanal em pequenos lotes.',
       22.90, 35, '/static/images/produtos/cerveja_ipa.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Cerveja IPA Artesanal'
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque, imagem_url, data_criacao)
SELECT 'Licor de Café',
       'Licor cremoso com intenso sabor de café e notas de baunilha. Perfeito para sobremesas.',
       45.90, 18, '/static/images/produtos/licor_cafe.jpg', NOW()
FROM dual
WHERE NOT EXISTS (
    SELECT * FROM produtos WHERE nome = 'Licor de Café'
);