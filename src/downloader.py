import os
import httpx
import asyncio

class Downloader:
    def __init__(self, lista_de_dados: list, pasta_destino: str = "boletos"):
        self.lista_de_dados = lista_de_dados
        self.pasta_destino = pasta_destino

        os.makedirs(self.pasta_destino, exist_ok=True)
        print(f"Downloader inicializando. Os arquivos serão salvos em '{self.pasta_destino}/'")

    async def _download_boleto(self, client: httpx.AsyncClient, dado: dict):
        url_relativa = dado.get("boleto_url")
        if not url_relativa:
            print(f"[AVISO] Registro '{dado['descricao']}' não possui URL de boleto.")
            return
        url_base = "https://arth-inacio.github.io/scod_scraping_challenge/"
        url_completa = f"{url_base}{url_relativa}"
        nome_arquivo = os.path.basename(url_relativa)
        caminho_arquivo = os.path.join(self.pasta_destino, nome_arquivo)

        try: 
            response = await client.get(url_completa, timeout = 30.0)
            response.raise_for_status()
            with open(caminho_arquivo, "wb") as f:
                f.write(response.content)
            print(f"[SUCESSO] Boleto '{nome_arquivo}' baixado.")
        except httpx.RequestError as e:
            print(f"[ERROR] Falha ao baixar o boleto de {e.request.url}. Erro: {e}")

    async def run(self):
        print("Iniciando o processo de download assincrono...")
        async with httpx.AsyncClient() as client: 
            tarefas =[]
            for dado in self.lista_de_dados:
                tarefa = self._download_boleto(client, dado)
                tarefas.append(tarefa)
            await asyncio.gather(*tarefas)
        print("Processo de download finalizado.")
    
if __name__ == '__main__':
    dados_de_teste = [
    {"descricao": "IPTU", "boleto_url": "boletos/30000001.pdf"},
    {"descricao": "Taxa de Lixo", "boleto_url": "boletos/30000003.pdf"},
    {"descricao": "Conta de Luz", "boleto_url": "boletos/30000004.pdf"}
    ]

    meu_downloader = Downloader(lista_de_dados=dados_de_teste)
    asyncio.run(meu_downloader.run())