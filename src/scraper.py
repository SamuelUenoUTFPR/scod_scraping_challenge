import requests 
from bs4 import BeautifulSoup 

class Scraper: 
    def __init__(self, url: str): 
        self.url = url 
        self.dados_extraidos = [] 
        print(f"Scraper inicializando para a URL: {self.url}") 
    
    def run(self):
        print("Iniciando o processo de scraping") 
        html = self._buscar_html()
        if html:
            self._analisar_dados(html)
        
        print("Scraping finalizado. Total de {len(self.dados_extraidos)} registros coletados.")
        return self.dados_extraidos 

    def _buscar_html(self) -> str | None: 
        try: 
            print(f"Buscando conteúdo de {self.url}...") 
            headers = { 
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(self.url, headers=headers, timeout=10) 
            response.raise_for_status() 
            return response.text 
        except requests.RequestException as e: 
            print(f"Erro ao buscar HTML: {e}")
            return None 
        
    def _analisar_dados(self, html_content: str): 
        print("Analisando o conteúdo HTML...")
        soup = BeautifulSoup(html_content, 'lxml') 
        linhas_tabela = soup.select('tbody tr') 
        print(f"Encontradas {len(linhas_tabela)} linhas na tabela.")

        for linha in linhas_tabela: 
            colunas = linha.find_all('td') 
            if len(colunas) == 7:
                try:
                    descricao = colunas[0].get_text(strip=True)
                    exercicio_str = colunas[1].get_text(strip=True)
                    parcela = colunas[2].get_text(strip=True)
                    vencimento = colunas[3].get_text(strip=True)
                    valor_str = colunas[4].get_text(strip=True)
                    status = colunas[5].get_text(strip=True)

                    tag_a_boleto = colunas[6].find('a')
                    link_boleto = tag_a_boleto.get('href') if tag_a_boleto else None

                    exercicio = int(exercicio_str)

                    valor_limpo = valor_str.replace("R$", "").strip().replace(",", ".")
                    valor = float(valor_limpo)

                    dado = {
                        "descricao": descricao,
                        "exercicio": exercicio,
                        "parcela": parcela,
                        "vencimento": vencimento,
                        "valor": valor,
                        "status": status,
                        "boleto_url": link_boleto
                    }
                    self.dados_extraidos.append(dado)
                except (ValueError, IndexError) as e:
                    print(f"Erro ao processar uma linha da tabela: {e}")
        
if __name__ == '__main__':
    URL_ALVO = "https://arth-inacio.github.io/scod_scraping_challenge/"
    meu_scraper = Scraper(url=URL_ALVO)
    dados = meu_scraper.run()

    if dados:
        print("\n--- DADOS EXTRAIDOS ---")
        import json
        print(json.dumps(dados[0], indent=2, ensure_ascii=False))
                
