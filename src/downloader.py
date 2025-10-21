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
        """
            Este metodo baixa um arquivo PDF de forma assincrona, sendo chamado como uma tarefa pelo asyncio.gather.
            Ele lida com a logica de um unico download, construçao de url, requisicao e salvamento do arquivo.
            Args:
                client (httpx.AsyncClient): sessao do cliente http.
                dado (dict): dicionario de dados de um unico registro, contem as chaves do boleto_url e descricao.
        """
        url_relativa = dado.get("boleto_url")
        if not url_relativa:
            logger.warning(f"[AVISO] Registro '{dado['descricao']}' não possui URL de boleto.")
            return
        # O link na tabela e relativo, entao eu precisei construir a url absoluta para a requisicao.
        url_base = "https://arth-inacio.github.io/scod_scraping_challenge/"
        url_completa = f"{url_base}{url_relativa}"
        nome_arquivo = os.path.basename(url_relativa) # basename extrai com segurança o nome do arquivo da url, pegando o nome base.
        caminho_arquivo = os.path.join(self.pasta_destino, nome_arquivo) 

        try: 
            response = await client.get(url_completa, timeout = 30.0) # o await pausa a função e libera o asyncio para trabalhar em outras tarefas
            response.raise_for_status() # de download enquanto esta aqui espera pela rede.
            logger.debug(f"-> Tentando salvar o arquivo como: '{caminho_arquivo}'")
            with open(caminho_arquivo, "wb") as f: # wb (write binary) abre o arquivo em modo binario. que trata os dados como bytes brutos em vez de texto.
                f.write(response.content)
            logger.info(f"[SUCESSO] Boleto '{nome_arquivo}' baixado.")
        except httpx.RequestError as e:
            logger.exception(f"[ERROR] Falha ao baixar o boleto de {e.request.url}.")

    async def run(self):
        """
            Metodo principal que realiza o download assincrono, criando um pool de conexoes com o asyncClient e 
            preparando uma lista das tarefas de download que tem que ser executadas, posteriormente, usei asyncio.gather
            para executa-las concorrentemente.
        """
        logger.info("Iniciando o processo de download assincrono...")
        async with httpx.AsyncClient() as client: 
            tarefas =[] # lista de tarefas a serem executadas.
            for dado in self.lista_de_dados:
                tarefa = self._download_boleto(client, dado)
                tarefas.append(tarefa)
            await asyncio.gather(*tarefas) # comando que executa todas as tarefas da lista concorrentemente e espera que elas terminem. * desempacota a lista tarefas em argumentos individuais.
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