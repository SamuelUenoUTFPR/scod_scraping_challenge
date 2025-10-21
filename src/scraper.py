"""
Módulo Scraper - Responsável pela Coleta de Dados da Página Web.

Este módulo contém a classe Scraper, que encapsula toda a lógica 
necessária para se conectar à página-alvo do desafio, baixar seu 
conteúdo HTML e extrair os dados da tabela de débitos.

A escolha de 'requests' + 'BeautifulSoup' foi feita por ser a 
abordagem mais leve e eficiente, dado que a página-alvo é 
estática.
"""

import requests 
from bs4 import BeautifulSoup 
from .utils import formatar_valor_monetario
import logging

logger = logging.getLogger(__name__)

class Scraper: 
    """
    Classe principal para realizar o scraping da tabela de débitos.
    Ela e responsavel por se conectar com a url do desafio, baixar o conteudo html da pagina 
    e analisar o html para extrair os dados de cada linha da tabela.
    Utiliza requests para as requisições HTTP e BeautifulSoup para a análise do DOM, com lxml como parser.
    """
    def __init__(self, url: str): 
        """
            Esta função e o metodo construtor da classe, ela inicializa uma nova instância do Scraper
            e cria os objetos url e dados_extraidos, tambem lança uma mensagem de inicializaçao da classe.
            Args: url (str): A URL completa da página-alvo.
        """
        self.url = url 
        self.dados_extraidos = [] 
        logger.info(f"Scraper inicializando para a URL: {self.url}") 
    
    def run(self):
        """
            Esta função inicia o processo de busca da pagina html, acionando as funções _buscar_html para 
            obter o conteudo da pagina e _analisar_dados para processar o html e preencher a lista de dados,
            retornando uma mensagem de finalização e todos os dados que foram
            extraidos no processo de busca e analise dos dados, serve para dar o start.
            Returns: Uma lista de dicionaris, onde cada dicionario representa uma linha de 
            debito extraida da tabela.
        """
        logger.info("Iniciando o processo de scraping") 
        html = self._buscar_html()
        if html: # So prossegue se o html for baixado com sucesso.
            self._analisar_dados(html)
        
        logger.info(f"Scraping finalizado. Total de {len(self.dados_extraidos)} registros coletados.")
        return self.dados_extraidos 

    def _buscar_html(self) -> str | None: 
        """
            Esta função realiza a busca no conteudo da pagina principal, conectando-se a url alvo e baixando o conteudo html,
            alocando um header de User-Agent para evitar possiveis bloqueios de segurança e utilizando um tempo maximo de 10 segundos, 
            que previne que o script fique preso indefinidamente caso o site demore para responder,
            retornando o status da requisição, caso resulte em sucesso (2xx) ou erro (4xx ou 5xx).
            Returns: str | None: O conteudo html da pagina como string em caso de sucesso, ou None
            em caso de falha.
        """
        try: 
            logger.info(f"Buscando conteúdo de {self.url}...") 
            headers = { 
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            } # Alocação padrao de user-agent
            response = requests.get(self.url, headers=headers, timeout=10) 
            response.raise_for_status() # Fiz essa função para retornar o status da requisição, caso de algo na faixa de 2xx, sucesso, else = ERRO, caindo no except.
            return response.text 
        except requests.RequestException as e: 
            logger.exception(f"Erro ao buscar HTML: {self.url}")
            return None 
        
    def _analisar_dados(self, html_content: str): 
        """
            Esta função utiliza a biblioteca BeautifulSoup para fazer a analise do html bruto para extrair os dados da tabela
            com o parser lxml (mais rapido que o 'html.parser') para navegar na estrutura do DOM.
            Args: html_content (str): A string de conteudo html baixada pelo metodo _buscar_html
        """
        logger.info("Analisando o conteúdo HTML...")
        soup = BeautifulSoup(html_content, 'lxml') 
        linhas_tabela = soup.select('tbody tr') # O seletor tbody tr e usado para pegar todas as linhas (tr) de dados, ignorando o cabeçalho (thead)
        logger.info(f"Encontradas {len(linhas_tabela)} linhas na tabela.")

        for linha in linhas_tabela: # Este laço organiza os dados de todas as linhas encontradas, linha a linha, formando uma tabela 
            colunas = linha.find_all('td') # Seleciona todas as celulas (td) da linha atual
            if len(colunas) == 7: # tem que ser igual a 7 colunas, para ter a estrutura esperada antes de tentar acessa-la
                try:
                    descricao = colunas[0].get_text(strip=True) # Extração de texto de cada coluna
                    exercicio_str = colunas[1].get_text(strip=True) # strip=True limpa espaços em branco 
                    parcela = colunas[2].get_text(strip=True)
                    vencimento = colunas[3].get_text(strip=True)
                    valor_str = colunas[4].get_text(strip=True)
                    status = colunas[5].get_text(strip=True)

                    tag_a_boleto = colunas[6].find('a') # Fiz desse modo para facilitar a obtenção do link dos pdfs dos boletos, com o alvo da busca sendo
                    link_boleto = tag_a_boleto.get('href') if tag_a_boleto else None # a tag 'a' e seu atributo 'href'

                    exercicio = int(exercicio_str)

                    valor = formatar_valor_monetario(valor_str)

                    dado = { # Monta o dicionario com os dados limpos e formatados
                        "descricao": descricao,
                        "exercicio": exercicio,
                        "parcela": parcela,
                        "vencimento": vencimento,
                        "valor": valor,
                        "status": status,
                        "boleto_url": link_boleto
                    }
                    self.dados_extraidos.append(dado) 
                except (ValueError, IndexError) as e: # Captura erros que podem ocorrer na conversão, permitindo que o 
                    logger.exception(f"Erro ao processar uma linha da tabela: {e}") # scraper continue nas proximas linhas.
        
# Bloco de Depuração, teste e manutenção:
if __name__ == '__main__':
    URL_ALVO = "https://arth-inacio.github.io/scod_scraping_challenge/"
    meu_scraper = Scraper(url=URL_ALVO)
    dados = meu_scraper.run()

    if dados:
        print("\n--- DADOS EXTRAIDOS ---")
        import json
        print(json.dumps(dados[0], indent=2, ensure_ascii=False))
                
