"""
Módulo de serviço para operações relacionadas a produtos.
Segue o padrão Service do DDD, implementando casos de uso
relacionados ao gerenciamento de produtos no sistema.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import pandas as pd
from io import BytesIO
import tempfile

from backend.domain.models.produto import Produto
from backend.infrastructure.interfaces.repositories.produto_repository import ProdutoRepository


class ProdutoService:
    """
    Serviço para gerenciamento de produtos no sistema.
    Implementa casos de uso relacionados a produtos.
    """
    
    def __init__(self):
        """
        Inicializa o serviço de produtos.
        """
        self.produto_repository = ProdutoRepository()
    
    def listar_produtos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os produtos ativos no sistema.
        
        Returns:
            List[Dict[str, Any]]: Lista de produtos em formato de dicionário
        """
        produtos = self.produto_repository.listar_todos()
        return [produto.to_dict() for produto in produtos]
    
    def obter_produto_por_id(self, produto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um produto pelo seu ID.
        
        Args:
            produto_id (int): ID do produto a ser obtido
            
        Returns:
            Optional[Dict[str, Any]]: Produto encontrado ou None
        """
        produto = self.produto_repository.obter_por_id(produto_id)
        return produto.to_dict() if produto else None
    
    def criar_produto(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo produto no sistema.
        
        Args:
            dados (Dict[str, Any]): Dados do produto a ser criado
            
        Returns:
            Dict[str, Any]: Produto criado com ID atribuído
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        # Validações e criação do produto
        try:
            produto = Produto(
                id=None,
                nome=dados.get('nome'),
                descricao=dados.get('descricao', ''),
                preco=float(dados.get('preco', 0)),
                quantidade_estoque=int(dados.get('quantidade_estoque', 0)),
                imagem_url=dados.get('imagem_url')
            )
            
            produto = self.produto_repository.criar(produto)
            return produto.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar produto: {str(e)}")
    
    def atualizar_produto(self, produto_id: int, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um produto existente.
        
        Args:
            produto_id (int): ID do produto a ser atualizado
            dados (Dict[str, Any]): Novos dados do produto
            
        Returns:
            Dict[str, Any]: Produto atualizado
            
        Raises:
            ValueError: Se o produto não existir ou os dados forem inválidos
        """
        produto = self.produto_repository.obter_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado")
            
        # Atualizar apenas os campos fornecidos
        if 'nome' in dados:
            produto.nome = dados['nome']
        if 'descricao' in dados:
            produto.descricao = dados['descricao']
        if 'preco' in dados:
            produto.preco = float(dados['preco'])
        if 'quantidade_estoque' in dados:
            produto.quantidade_estoque = int(dados['quantidade_estoque'])
        if 'imagem_url' in dados:
            produto.imagem_url = dados['imagem_url']
            
        produto = self.produto_repository.atualizar(produto)
        return produto.to_dict()
    
    def excluir_produto(self, produto_id: int) -> bool:
        """
        Exclui (logicamente) um produto do sistema.
        
        Args:
            produto_id (int): ID do produto a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
            
        Raises:
            ValueError: Se o produto não existir
        """
        produto = self.produto_repository.obter_por_id(produto_id)
        if not produto:
            raise ValueError(f"Produto com ID {produto_id} não encontrado")
            
        return self.produto_repository.excluir(produto_id)
    
    def processar_imagem_produto(self, imagem, diretorio_upload: str) -> Optional[str]:
        """
        Processa o upload de uma imagem para um produto.
        
        Args:
            imagem: Objeto de arquivo da imagem enviada
            diretorio_upload (str): Caminho para o diretório de upload
            
        Returns:
            Optional[str]: URL da imagem ou None se não houver imagem
        """
        if not imagem or imagem.filename == '':
            return None
            
        filename = secure_filename(f"{uuid.uuid4().hex}_{imagem.filename}")
        filepath = os.path.join(diretorio_upload, filename)
        imagem.save(filepath)
        
        # Retornar caminho relativo para a imagem
        return f"/static/images/produtos/{filename}"
        
    def exportar_estoque_para_excel(self) -> str:
        """
        Exporta todos os produtos do estoque para uma planilha Excel.
        
        Returns:
            str: Caminho do arquivo Excel gerado
            
        Raises:
            Exception: Se ocorrer um erro ao gerar o arquivo
        """
        try:
            # Obter todos os produtos ativos
            produtos = self.produto_repository.listar_todos()
            
            # Converter produtos para lista de dicionários para o pandas
            dados_produtos = []
            for produto in produtos:
                dados_produtos.append({
                    "ID": produto.id,
                    "Nome": produto.nome,
                    "Descrição": produto.descricao,
                    "Preço (R$)": produto.preco,
                    "Quantidade em Estoque": produto.quantidade_estoque,
                    "Valor Total (R$)": produto.preco * produto.quantidade_estoque,
                    "URL da Imagem": produto.imagem_url
                })
            
            # Criar DataFrame pandas
            df = pd.DataFrame(dados_produtos)
            
            # Criar diretório para exportações se não existir
            diretorio_export = os.path.join(os.getcwd(), "backend", "static", "exports")
            os.makedirs(diretorio_export, exist_ok=True)
            
            # Gerar nome de arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"estoque_{timestamp}.xlsx"
            caminho_arquivo = os.path.join(diretorio_export, nome_arquivo)
            
            # Criar um ExcelWriter
            writer = pd.ExcelWriter(caminho_arquivo, engine='xlsxwriter')
            
            # Escrever o DataFrame no Excel
            df.to_excel(writer, sheet_name='Estoque', index=False)
            
            # Acessar a planilha e o workbook
            workbook = writer.book
            worksheet = writer.sheets['Estoque']
            
            # Definir formatos
            formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
            formato_quantidade = workbook.add_format({'num_format': '#,##0'})
            formato_cabecalho = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Aplicar formatos
            worksheet.set_column('D:D', 15, formato_moeda)  # Preço
            worksheet.set_column('E:E', 15, formato_quantidade)  # Quantidade
            worksheet.set_column('F:F', 15, formato_moeda)  # Valor Total
            worksheet.set_column('A:A', 8)   # ID
            worksheet.set_column('B:B', 30)  # Nome
            worksheet.set_column('C:C', 40)  # Descrição
            worksheet.set_column('G:G', 40)  # URL da Imagem
            
            # Aplicar formato de cabeçalho
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, formato_cabecalho)
            
            # Adicionar filtros
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            
            # Adicionar uma linha de totais no final
            row_totais = len(df) + 2
            worksheet.write(row_totais, 0, 'TOTAIS', workbook.add_format({'bold': True}))
            worksheet.write_formula(row_totais, 4, f'=SUM(E2:E{len(df)+1})', formato_quantidade)
            worksheet.write_formula(row_totais, 5, f'=SUM(F2:F{len(df)+1})', formato_moeda)
            
            # Adicionar data de geração
            worksheet.write(row_totais + 2, 0, f'Relatório gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
            
            # Salvar o arquivo
            writer.close()
            
            # Retornar caminho do arquivo para download
            return f"/static/exports/{nome_arquivo}"
            
        except Exception as e:
            raise Exception(f"Erro ao exportar estoque para Excel: {str(e)}")

    def exportar_estoque_para_excel_bytes(self) -> BytesIO:
        """
        Exporta todos os produtos do estoque para um objeto BytesIO contendo uma planilha Excel.
        Útil para retornar diretamente como resposta HTTP sem salvar arquivo.
        
        Returns:
            BytesIO: Objeto contendo o arquivo Excel em memória
            
        Raises:
            Exception: Se ocorrer um erro ao gerar o arquivo
        """
        try:
            # Obter todos os produtos ativos
            produtos = self.produto_repository.listar_todos()
            
            # Converter produtos para lista de dicionários para o pandas
            dados_produtos = []
            for produto in produtos:
                dados_produtos.append({
                    "ID": produto.id,
                    "Nome": produto.nome,
                    "Descrição": produto.descricao,
                    "Preço (R$)": produto.preco,
                    "Quantidade em Estoque": produto.quantidade_estoque,
                    "Valor Total (R$)": produto.preco * produto.quantidade_estoque,
                    "URL da Imagem": produto.imagem_url
                })
            
            # Criar DataFrame pandas
            df = pd.DataFrame(dados_produtos)
            
            # Criar objeto BytesIO para guardar o Excel em memória
            output = BytesIO()
            
            # Criar um ExcelWriter
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Escrever o DataFrame no Excel
                df.to_excel(writer, sheet_name='Estoque', index=False)
                
                # Acessar a planilha e o workbook
                workbook = writer.book
                worksheet = writer.sheets['Estoque']
                
                # Definir formatos
                formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
                formato_quantidade = workbook.add_format({'num_format': '#,##0'})
                formato_cabecalho = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D9E1F2',
                    'border': 1
                })
                
                # Aplicar formatos
                worksheet.set_column('D:D', 15, formato_moeda)  # Preço
                worksheet.set_column('E:E', 15, formato_quantidade)  # Quantidade
                worksheet.set_column('F:F', 15, formato_moeda)  # Valor Total
                worksheet.set_column('A:A', 8)   # ID
                worksheet.set_column('B:B', 30)  # Nome
                worksheet.set_column('C:C', 40)  # Descrição
                worksheet.set_column('G:G', 40)  # URL da Imagem
                
                # Aplicar formato de cabeçalho
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, formato_cabecalho)
                
                # Adicionar filtros
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
                
                # Adicionar uma linha de totais no final
                row_totais = len(df) + 2
                worksheet.write(row_totais, 0, 'TOTAIS', workbook.add_format({'bold': True}))
                worksheet.write_formula(row_totais, 4, f'=SUM(E2:E{len(df)+1})', formato_quantidade)
                worksheet.write_formula(row_totais, 5, f'=SUM(F2:F{len(df)+1})', formato_moeda)
                
                # Adicionar data de geração
                worksheet.write(row_totais + 2, 0, f'Relatório gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
            
            # Reposicionar o ponteiro para o início do arquivo em memória
            output.seek(0)
            
            return output
            
        except Exception as e:
            raise Exception(f"Erro ao exportar estoque para Excel: {str(e)}") 