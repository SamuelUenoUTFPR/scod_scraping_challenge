import os
import pdfplumber
import re

class Extractor:
    def __init__(self, pasta_boletos: str = "boletos"):
        self.pasta_boletos = pasta_boletos
        self.regex_linha_digitavel = re.compile(r'\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d+')
        print(f"Extractor inicializado para a pasta: '{self.pasta_boletos}'")

    