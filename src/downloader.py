"""
Modulo Downloader - Responsavel pelo download assincrono de boletos
Este modulo contem a classe Downloader, que encapsula toda a logica necessaria
para acessar os arquivos pdfs dos boletos, realizando o download de forma concorrente 
e retornando o status da tentativa.
A escolha do httpx e asyncio foi uma decisao de design para otimizar o desempenho,
visto que o codigo inicia multiplos downloados ao mesmo tempo, o que reduz o tempo total
de espera da rede.
"""

import os
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

class Downloader:
    """
        Classe principal para realizar o download concorrente dos arquivos pdfs.
        Ela e responsavel por receber a lista de dados do Scraper, criar um cliente http assincrono (httpx.AsyncClient),
        orquestrar o download de multiplos arquivos (asyncio.gather) e os salva na pasta de destino designada (boletos).
    """
    def __init__(self, lista_de_dados: list, pasta_destino: str = "boletos"):
        """
            Inicializa o Downloader.
            Args: lista_de_dados (list): Lista de dicionarios extraida pelo Scraper, cada um 
            contem a CHAVE boleto_url.
                  pasta_destino (str): Nome da pasta onde os pdfs serao salvos, se nao existir, sera criada.
        """
        self.lista_de_dados = lista_de_dados
        self.pasta_destino = pasta_destino

        os.makedirs(self.pasta_destino, exist_ok=True) # Garante que a pasta de destino exista; 
        logger.info(f"Downloader inicializando. Os arquivos serão salvos em '{self.pasta_destino}/'")

    async def _download_boleto(self, client: httpx.AsyncClient, dado: dict):
        url_relativa = dado.get("boleto_url")
        if not url_relativa:
            logger.warning(f"[AVISO] Registro '{dado['descricao']}' não possui URL de boleto.")
            return
        url_base = "https://arth-inacio.github.io/scod_scraping_challenge/"
        url_completa = f"{url_base}{url_relativa}"
        nome_arquivo = os.path.basename(url_relativa)
        caminho_arquivo = os.path.join(self.pasta_destino, nome_arquivo)

        try: 
            response = await client.get(url_completa, timeout = 30.0)
            response.raise_for_status()
            logger.debug(f"-> Tentando salvar o arquivo como: '{caminho_arquivo}")
            with open(caminho_arquivo, "wb") as f:
                f.write(response.content)
            logger.info(f"[SUCESSO] Boleto '{nome_arquivo}' baixado.")
        except httpx.RequestError as e:
            logger.exception(f"[ERROR] Falha ao baixar o boleto de {e.request.url}. Erro: {e}")

    async def run(self):
        logger.info("Iniciando o processo de download assincrono...")
        async with httpx.AsyncClient() as client: 
            tarefas =[]
            for dado in self.lista_de_dados:
                tarefa = self._download_boleto(client, dado)
                tarefas.append(tarefa)
            await asyncio.gather(*tarefas)
        logger.info("Processo de download finalizado.")

# Bloco de Depuração, teste e manutenção:
if __name__ == '__main__':
    dados_de_teste = [
    {"descricao": "IPTU", "boleto_url": "boletos/30000001.pdf"},
    {"descricao": "IPTU", "boleto_url": "boletos/30000002.pdf"},
    {"descricao": "IPTU", "boleto_url": "boletos/30000003.pdf"},
    {"descricao": "IPTU", "boleto_url": "boletos/30000004.pdf"}
    ]

    meu_downloader = Downloader(lista_de_dados=dados_de_teste)
    asyncio.run(meu_downloader.run())