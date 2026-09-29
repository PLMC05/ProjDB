from src.models import Bucket

class HashIndex:
    def __init__(self, total_registros: int, fator_registro_bucket: int):
        self.fr = fator_registro_bucket  # FR: Capacidade máxima do bucket
        self.nr = total_registros        # NR: Total de registros
        
        # NB > NR / FR
        self.nb = int((self.nr / self.fr) * 1.2) + 1 
        
        self.buckets = [Bucket(id=i, capacity=self.fr) for i in range(self.nb)]
        self.overflow_buckets = []
        
        self.colisoes = 0
        self.overflows = 0

    def funcao_hash_propria(self, chave: str) -> int:
        h = 0
        for ch in chave.lower():
            h = (h * 31 + ord(ch)) % self.nb
        return h

    def _get_overflow(self, oid: int) -> Bucket:
        return self.overflow_buckets[oid]

    def construir_indice(self, paginas):
        for pagina in paginas:
            for palavra in pagina.registros:
                bid = self.funcao_hash_propria(palavra)
                self._insert(bid, palavra, pagina.numero)

    def _insert(self, bid: int, key: str, page_id: int):
        bucket = self.buckets[bid]
        current = bucket
        
        while True:
            if len(current.entries) < current.capacity:
                current.entries.append((key, page_id))
                return
            if current.overflow_chain:
                next_id = current.overflow_chain[0]
                current = self._get_overflow(next_id)
            else:
                break

        self.colisoes += 1
        if len(bucket.entries) == bucket.capacity:
            self.overflows += 1

        ob = Bucket(id=len(self.overflow_buckets), capacity=self.fr)
        ob.entries.append((key, page_id))
        self.overflow_buckets.append(ob)
        current.overflow_chain.append(ob.id)