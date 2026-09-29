class Pagina:
    def __init__(self, numero: int):
        self.numero = numero
        self.registros = []  # Lista de palavras (strings)

    def adicionar_registro(self, registro: str):
        self.registros.append(registro)

    def __repr__(self):
        return f"Pagina(num={self.numero}, total_regs={len(self.registros)})"


class Bucket:
    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity                              # FR (Fator de Registro)
        self.entries = []                                     # Lista de tuplas [(chave, page_id)]
        self.overflow_chain = []                              # IDs de buckets de overflow encadeados

    def esta_cheio(self) -> bool:
        return len(self.entries) >= self.capacity