import requests # importa a biblioteca requests para fazer requisições HTTP
from bs4 import BeautifulSoup # importa a biblioteca BeautifulSoup para fazer parsing de HTML

class Scraper: # Cria a classe Scraper para encapsular a lógica de scraping
    def __init__(self, url: str): # O método __init__ é o construtor da classe, que inicializa a instância com a URL fornecida
        self.url = url # Atributo que armazena a URL a ser raspada
        self.dados_extraidos = [] # Atributo que armazenará os dados extraídos
        print(f"Scraper inicializando para a URL: {self.url}") # Mensagem de inicialização
    
    def run(self): # Método principal para iniciar o processo de scraping
        print("Iniciando o processo de scraping") 
        # Logica depois eu vou colocar aqui
        print("Scraping finalizado.")
        return self.dados_extraidos # Retorna os dados extraídos

    def _buscar_html(self) -> str | None: # O _ indica que este metodo é para uso interno da classe
        try: # Essencial para tratar erros de conexão e timeout
            print(f"Buscando conteúdo de {self.url}...") 
            headers = { # Define um cabeçalho de requisição para simular um navegador real
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(self.url, headers=headers, timeout=10) # Faz a requisição GET com um timeout de 10 segundos
            response.raise_for_status() # Lança um erro para status HTTP 4xx ou 5xx, uma forma de verificar se a requisição foi bem sucedida (status 200)
            return response.text # Retorna o conteúdo HTML da página
        except requests.RequestException as e: # Essencial para tratart erros de conexão e timeout
            print(f"Erro ao buscar HTML: {e}")
            return None 
        
    def _analisar_dados(self, html_content: str): # Método para analisar o conteúdo HTML e extrair dados
        print("Analisando o conteúdo HTML...")
        soup = BeautifulSoup(html_content, 'lxml') # Usa o parser lxml para analisar o HTML
        linhas_tabela = soup.select('tbody tr') # Seleciona todas as linhas dentro do corpo da tabela
        print(f"Encontradas {len(linhas_tabela)} linhas na tabela.")

        for linha in linhas_tabela: # Itera sobre cada linha da tabela
            colunas = linha.find_all('td') # Extrai todas as colunas (td) da linha
            if len(colunas) >= 7:  # Verifica se há colunas suficientes
                dado = {
                    'coluna1': colunas[0].get_text(strip=True),
                    'coluna2': colunas[1].get_text(strip=True),
                    'coluna3': colunas[2].get_text(strip=True),
                    'coluna4': colunas[3].get_text(strip=True),
                    'coluna5': colunas[4].get_text(strip=True),
                }
                self.dados_extraidos.append(dado)
                
