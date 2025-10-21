"""
    Módulo principal, sendo o entrypoint do projeto. Ele não executa nenhuma lógica, só coordena a execução das classes
    Scraper, Downloader e Extractor, na ordem correta para cumprir os requisitos do desafio.
    O fluxo de execução é: Configuração do logging para todo o projeto; execução do Scraper para extrair os dados da tabela HTML;
    execução do Downloader para baixar os boletos de forma assíncrona, execução do Extractor para ler os PDF e extrair as linhas digitáveis e,
    por fim, salvar o conjunto de dados final e completo em um arquivo JSON.
"""

import asyncio
import json
import os
import logging
from src.scraper import Scraper
from src.downloader import Downloader
from src.extractor import Extractor

logging.basicConfig(
    level = logging.INFO, # Coloquei para o logger mostrar apenas mensagens: INFO, WARNING, ERROR e CRITICAL. DEBUG sera ignorado.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Defini o formato de cada linha do log
    datefmt = '%Y-%m-%d %H:%M:%S', # Defini o formato das datas e horarios do log
    handlers=[
        logging.FileHandler("data/app.log", mode='w'), # Coloquei para enviar para os logs um arquivo em data/app.log. O mode = 'w' (write) faz com que o arquivo seja sobrescrito a cada nova execução, serve para usar em teste.
        logging.StreamHandler() # Envia os mesmos logs para o terminal.
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING) # Silenciei o httpx para manter o log mais limpo.
logger = logging.getLogger(__name__) # Defini um logger para esse arquivo em especifico, assim como fiz nas outras classes que utilizei o logger.
URL_ALVO = "https://arth-inacio.github.io/scod_scraping_challenge/"
PASTA_BOLETOS = "boletos"
ARQUIVO_JSON = "data/dados.json"

def main():
    """
        Função principal que executa o pipeline de scraping em 4 etapas.
    """
    logger.info("Iniciando o processo de Scraping...")
    logger.info("[Etapa 1/4] Iniciando a extração de dados na tabela...")
    scraper = Scraper(url=URL_ALVO)
    dados_tabela = scraper.run()

    if not dados_tabela: # Encerra o programa se a etapa mais crucial falhar.
        logger.error("Nenhum dado foi extraido, encerrando o processo.")
        return
    logger.info(f"Extração concluida, {len(dados_tabela)} registros encontrados")
    logger.info("\n[Etapa 2/4] Iniciando o download dos boletos...")
    downloader = Downloader(lista_de_dados=dados_tabela, pasta_destino=PASTA_BOLETOS)
    asyncio.run(downloader.run())
    logger.info("Download dos boletos concluido.")
    logger.info("\n[Etapa 3/4] Iniciando extração das linhas digitaveis...")
    extractor = Extractor(pasta_boletos=PASTA_BOLETOS)
    dados_finais = []
    for dado in dados_tabela: # Iteração sobre a lista de dados que o Scraper gerou
        nome_arquivo = os.path.basename(dado.get("boleto_url", ""))
        if nome_arquivo:
            linha_digitavel = extractor.extrair_linha_digitavel(nome_arquivo)
            dado["linha_digitavel"] = linha_digitavel
        else:
            dado["linha_digitavel"] = None
        dados_finais.append(dado)
    logger.info("Extração concluida")
    logger.info("\n[Etapa 4/4] Salvando dados finais em JSON...")
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True) # Adicionei para garantir que o subdiretorio data/ exista.
    try:
        with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f: 
            json.dump(dados_finais, f, indent=2, ensure_ascii=False) # json.dump escreve a estrutura de dados Python no arquivo e o indent=2 formata o JSON de forma legível.
        logger.info(f"Sucesso, dados salvos em '{ARQUIVO_JSON}'")
    except IOError as e:
        logger.exception(f"Erro ao salvar o arquivo JSON: {e}")
    logger.info("\n--- Processo Finalizado ---")
if __name__ == "__main__": # Ponto de entrada padrão do Python, o código so vai ser executado se o script for chamado diretamente.
    main()