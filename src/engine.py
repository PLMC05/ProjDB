import os
from src.models import Pagina

class Engine:
    def __init__(self):
        self.paginas = []
        self.total_registros = 0

    def carregar_e_paginar(self, caminho_arquivo: str, tamanho_pagina: int):
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado em: {caminho_arquivo}")
        
        if tamanho_pagina <= 0:
            raise ValueError("O tamanho da página deve ser maior que zero.")

        palavras = []
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            for linha in f:
                palavra = linha.strip()
                if palavra:
                    palavras.append(palavra)

        self.total_registros = len(palavras)
        self.paginas = []
        
        num_pagina_atual = 1
        for i in range(0, self.total_registros, tamanho_pagina):
            lote = palavras[i:i + tamanho_pagina]
            pagina = Pagina(numero=num_pagina_atual)
            for palavra in lote:
                pagina.adicionar_registro(palavra)
            self.paginas.append(pagina)
            num_pagina_atual += 1

        return self.total_registros, len(self.paginas)

    def obter_primeira_e_ultima_pagina(self):
        if not self.paginas:
            return None, None
        return self.paginas[0], self.paginas[-1]