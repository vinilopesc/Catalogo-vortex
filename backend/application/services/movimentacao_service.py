from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.domain.entities.movimentacao import Movimentacao, TipoMovimentacao
from backend.infrastructure.repositories.movimentacao_repository import MovimentacaoRepository
from backend.infrastructure.repositories.produto_repository import ProdutoRepository


class MovimentacaoService:
    """
    Serviço de aplicação para gerenciar movimentações de estoque.
    Implementa a lógica de negócio relacionada a entradas e saídas de produtos.
    """
    
    def __init__(self):
        self.movimentacao_repository = MovimentacaoRepository()
        self.produto_repository = ProdutoRepository()
    
    def registrar_movimentacao(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra uma nova movimentação de estoque e atualiza o estoque do produto.
        
        Args:
            dados: Dicionário com os dados da movimentação
            
        Returns:
            Dicionário com os dados da movimentação criada
            
        Raises:
            ValueError: Se o produto não existir ou dados inválidos
            Exception: Em caso de erro na criação
        """
        # Validar produto - primeiro tentamos obter apenas produtos ativos
        produto_id = dados.get("produto_id")
        
        # Primeiro verificamos se o produto existe (mesmo que tenha sido excluído)
        produto_histórico = self.produto_repository.obter_produto_mesmo_deletado(produto_id)
        if not produto_histórico:
            raise ValueError(f"Produto com ID {produto_id} não encontrado no sistema")
        
        # Agora verificamos se o produto está ativo (não excluído)
        produto = self.produto_repository.obter_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} foi excluído e não pode receber movimentações")
        
        # Validar quantidade
        quantidade = int(dados.get("quantidade", 0))
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
        
        # Validar tipo de movimentação
        tipo_str = dados.get("tipo")
        try:
            tipo = TipoMovimentacao(tipo_str)
        except ValueError:
            raise ValueError(f"Tipo de movimentação inválido: {tipo_str}")
        
        # Verificar estoque se for saída
        estoque_anterior = produto.quantidade_estoque
        if tipo == TipoMovimentacao.SAIDA and quantidade > estoque_anterior:
            raise ValueError(f"Estoque insuficiente. Disponível: {estoque_anterior} unidades")
        
        # Calcular novo estoque
        if tipo == TipoMovimentacao.ENTRADA:
            estoque_atual = estoque_anterior + quantidade
        else:  # SAIDA
            estoque_atual = estoque_anterior - quantidade
        
        # Criar objeto de movimentação
        movimentacao = Movimentacao(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            preco_unitario=float(dados.get("preco_unitario", 0)),
            data=datetime.fromisoformat(dados.get("data")) if dados.get("data") else datetime.now(),
            observacao=dados.get("observacao"),
            estoque_anterior=estoque_anterior,
            estoque_atual=estoque_atual
        )
        
        # Persistir movimentação
        movimentacao = self.movimentacao_repository.criar(movimentacao)
        
        # Atualizar estoque do produto
        produto.quantidade_estoque = estoque_atual
        try:
            self.produto_repository.atualizar(produto)
        except Exception as e:
            # Se falhar na atualização do produto, tentamos reverter a movimentação
            # Nota: isso poderia ser melhor implementado com um mecanismo de transação
            try:
                # Aqui poderíamos implementar uma lógica de reversão da movimentação
                # mas por simplicidade, apenas logamos o erro
                print(f"Erro ao atualizar estoque do produto: {str(e)}")
            except:
                pass
            # Propagar o erro original
            raise
        
        # Retornar dados da movimentação
        movimentacao_dict = movimentacao.to_dict()
        movimentacao_dict["produto_nome"] = produto.nome
        
        return movimentacao_dict
    
    def listar_movimentacoes(self) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações de estoque.
        
        Returns:
            Lista de dicionários com os dados das movimentações
        """
        return self.movimentacao_repository.listar_todos()
    
    def obter_movimentacao(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém uma movimentação pelo ID.
        
        Args:
            id: ID da movimentação
            
        Returns:
            Dicionário com os dados da movimentação ou None se não encontrada
        """
        movimentacao = self.movimentacao_repository.obter_por_id(id)
        if not movimentacao:
            return None
            
        movimentacao_dict = movimentacao.to_dict()
        
        # Obter nome do produto - aqui usamos o método que busca mesmo deletados
        produto = self.produto_repository.obter_produto_mesmo_deletado(movimentacao.produto_id)
        if produto:
            movimentacao_dict["produto_nome"] = produto.nome
            # Adicionar flag indicando se o produto foi excluído
            produto_ativo = self.produto_repository.obter_por_id(movimentacao.produto_id) is not None
            movimentacao_dict["produto_ativo"] = produto_ativo
        else:
            movimentacao_dict["produto_nome"] = "Produto não encontrado"
            movimentacao_dict["produto_ativo"] = False
            
        return movimentacao_dict
    
    def listar_movimentacoes_por_produto(self, produto_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as movimentações de um produto específico.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Lista de dicionários com os dados das movimentações
        """
        # Verificar se o produto existe, mesmo que tenha sido excluído
        produto = self.produto_repository.obter_produto_mesmo_deletado(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado no sistema")
            
        movimentacoes = self.movimentacao_repository.listar_por_produto(produto_id)
        
        # Adicionar informação sobre o status do produto (ativo ou excluído)
        produto_ativo = self.produto_repository.obter_por_id(produto_id) is not None
        for movimentacao in movimentacoes:
            movimentacao["produto_ativo"] = produto_ativo
            
        return movimentacoes 