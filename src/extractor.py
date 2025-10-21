"""
Modulo Extractor, responsavel pela extraçao de dados dos arquivos PDF.
Contem a classe Extractor, cuja responsabilidade é abrir os arquivos PDF de boletos baixados e extrair a linha digitável.
Para fazer isso, utilizei a biblioteca pdfplumber para a leitura do texto do PDF e o modulo re (regular expressions) para
localizar padrões específicos das linhas digitáveis dentro do texto extraído.
"""

import os
import pdfplumber
import re
import logging

logger = logging.getLogger(__name__)

class Extractor:
    """
        Classe que extrai a linha digitavel dos boletos.
        Encapsula a logica de abrir, ler e analisar o texto dos arquivos PDF usando uma expressão
        regular (regex) pre compilada.
    """
    def __init__(self, pasta_boletos: str = "boletos"):
        """
            Inicializa o extractor.
            Args: pasta_boletos (str): O diretorio onde os aqruivos PDF estão localizados.
        """
        self.pasta_boletos = pasta_boletos
        # o regex é compilado no método construtor para que nao seja recompilado a cada chamada no método 'extrair_linha_digitavel'.
        self.regex_linha_digitavel = re.compile(r'\d+\s\d+\s\d+\s\d+\s\d+') # defini essa regex após analisar as linhas digitáveis nos PDFs.
        logger.info(f"Extractor inicializado para a pasta: '{self.pasta_boletos}'")

    def extrair_linha_digitavel(self, nome_arquivo: str) -> str | None:
        """
            Abre apenas um PDF, extraindo todo o texto e procurando pela linha digitavel.
            Args: nome_arquivo (str): O nome do arquivo PDF localizado na pasta_boletos.
            Returns: str | None: String da linha digitavel encontrada ou None se o padrao não for encontrado ou caso ocorra erros.
        """
        caminho_completo = os.path.join(self.pasta_boletos, nome_arquivo)
        try:
            with pdfplumber.open(caminho_completo) as pdf: # Usei o pdfplumber.open atrelado a um with para garantir que o arquivo seja aberto e fechado corretamente.
                texto_completo = ""
                for pagina in pdf.pages: # Usei um laço para garantir a iteração de todas as páginas do PDF, mesmo que os PDF do teste sejam de página única, tornando o código mais robusto.
                    texto_completo += pagina.extract_text()
                match = self.regex_linha_digitavel.search(texto_completo) # Encontra o padrão da regex no texto.
                if match:
                    linha_digitavel = match.group(0) # retorna o texto completo que correspondeu ao padrao regex.
                    logger.info(f"[SUCESSO] Linha digitável encontrada em '{nome_arquivo}'.")
                    return linha_digitavel
            logger.warning(f"[AVISO] Linha digitável não encontrada em '{nome_arquivo}'.")
            return None
        except Exception as e: # Usei uma captura genérica de erro para caso um PDF esteja corrompido ou ilegível.
            logger.exception(f"[ERRO] Falha ao processar o arquivo '{nome_arquivo}'.")
            return None

# Bloco de Depuração, teste e manutenção:
if __name__ == '__main__':
    pasta_teste = "boletos"
    meu_extractor = Extractor(pasta_boletos=pasta_teste)
    arquivos_pdf = [f for f in os.listdir(pasta_teste) if f.endswith(".pdf")]
    if not arquivos_pdf:
        print("Nenhum PDF encontrado na pasta de boletos para teste.")
    else:
        primeiro_pdf = arquivos_pdf[0]
        print(f"\n--- Testando extração para o arquivo: {primeiro_pdf} ---")
        linha = meu_extractor.extrair_linha_digitavel(primeiro_pdf)
        if linha:
            print(f"\nLinha Digitável Extraída: {linha}")