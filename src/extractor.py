import os
import pdfplumber
import re

class Extractor:
    def __init__(self, pasta_boletos: str = "boletos"):
        self.pasta_boletos = pasta_boletos
        self.regex_linha_digitavel = re.compile(r'\d+\s\d+\s\d+\s\d\s\d+')
        print(f"Extractor inicializado para a pasta: '{self.pasta_boletos}'")

    def extrair_linha_digitavel(self, nome_arquivo: str) -> str | None:
        caminho_completo = os.path.join(self.pasta_boletos, nome_arquivo)
        try:
            with pdfplumber.open(caminho_completo) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto_completo += pagina.extract_text()
                match = self.regex_linha_digitavel.search(texto_completo)
                if match:
                    linha_digitavel = match.group(0)
                    print(f"[SUCESSO] Linha digitável encontrada em '{nome_arquivo}'.")
                    return linha_digitavel
            print(f"[AVISO] Linha digitável não encontrada em '{nome_arquivo}'.")
            return None
        except Exception as e:
            print(f"[ERRO] Falha ao processar o arquivo '{nome_arquivo}': {e}")
            return None

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