class Metrics:
    
    @staticmethod
    def calcular_taxa_colisoes(total_registros: int, total_colisoes: int) -> float:
        if total_registros == 0:
            return 0.0
        return (total_colisoes / total_registros) * 100

    @staticmethod
    def calcular_taxa_overflows(total_buckets: int, total_overflows: int) -> float:
        if total_buckets == 0:
            return 0.0
        return (total_overflows / total_buckets) * 100

    @staticmethod
    def estimar_custo_indice() -> int:
        return 2

    @staticmethod
    def estimar_custo_table_scan(numero_pagina_encontrada: int) -> int:
        return numero_pagina_encontrada