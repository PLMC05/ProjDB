import time
import html
import streamlit as st
from src.engine import Engine
from src.hash_index import HashIndex
from src.metrics import Metrics

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Simulador de Índice Hash Estático",
    page_icon="🗄️",
    layout="wide"
)

# --- INJEÇÃO DE ESTILO CSS PARA A GRADE DE BUCKETS ---
st.markdown("""
<style>
.bucket-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 8px;
    margin-top: 8px;
}
.bucket-card {
    background: #0f0f1c;
    border: 1px solid #252540;
    border-radius: 8px;
    padding: 10px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}
.bucket-card.overflow {
    border-color: #ef4444;
    background: #1c0f0f;
}
.bucket-card.highlighted {
    border-color: #7c6af7;
    background: #13102a;
    box-shadow: 0 0 0 1px #7c6af7;
}
.bucket-id {
    color: #4a5568;
    font-size: 0.65rem;
    margin-bottom: 4px;
}
.bucket-entry {
    color: #a0aec0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bucket-fill {
    height: 3px;
    border-radius: 2px;
    margin-top: 6px;
    background: #1e1e30;
}
.bucket-fill-bar {
    height: 100%;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

st.title("🗄️ Simulador de Índice Hash Estático (SGBD)")
st.markdown("Trabalho prático de Organização e Recuperação de Dados - Universidade de Fortaleza")

# Inicializando o estado da sessão para manter os dados carregados
if "engine" not in st.session_state:
    st.session_state.engine = None
if "hash_index" not in st.session_state:
    st.session_state.hash_index = None
if "index_construido" not in st.session_state:
    st.session_state.index_construido = False
if "ultimo_bucket_buscado" not in st.session_state:
    st.session_state.ultimo_bucket_buscado = None

# --- BARRA LATERAL (Configurações e Carga) ---
st.sidebar.header("⚙️ Configurações do Sistema")

caminho_padrao = "data/words.txt"
caminho_arquivo = st.sidebar.text_input("Caminho do Arquivo TXT", value=caminho_padrao)
tamanho_pagina = st.sidebar.number_input("Tamanho da Página (Registros / Página)", min_value=1, value=1000, step=100)
fator_bucket = st.sidebar.number_input("Capacidade do Bucket (FR)", min_value=1, value=50, step=5)

if st.sidebar.button("🚀 Carregar Dados e Construir Índice"):
    with st.spinner("Carregando arquivo e construindo índice hash..."):
        try:
            engine = Engine()
            total_regs, total_paginas = engine.carregar_e_paginar(caminho_arquivo, tamanho_pagina)
            
            # Criando o índice hash
            hash_idx = HashIndex(total_registros=total_regs, fator_registro_bucket=fator_bucket)
            
            inicio_tempo = time.time()
            hash_idx.construir_indice(engine.paginas)
            tempo_construcao = time.time() - inicio_tempo
            
            # Salvando no session_state
            st.session_state.engine = engine
            st.session_state.hash_index = hash_idx
            st.session_state.index_construido = True
            st.session_state.tempo_construcao = tempo_construcao
            st.session_state.ultimo_bucket_buscado = None
            
            st.sidebar.success(f"Sucesso! {total_regs} registros divididos em {total_paginas} páginas.")
            st.sidebar.info(f"Tempo de construção do índice: {tempo_construcao:.4f} segundos.")
        except Exception as e:
            st.sidebar.error(f"Erro ao processar: {e}")

# --- CORPO PRINCIPAL ---
if not st.session_state.index_construido:
    st.warning("⚠️ Por favor, configure os parâmetros na barra lateral e clique em **'Carregar Dados e Construir Índice'** para começar.")
else:
    engine = st.session_state.engine
    hash_idx = st.session_state.hash_index

    # Abas principais da interface
    aba1, aba2, aba3, aba4 = st.tabs([
        "📊 Visão Geral e Páginas", 
        "🪣 Visualização dos Buckets", 
        "🔍 Buscas (Índice vs Table Scan)", 
        "📈 Estatísticas e Métricas"
    ])

    with aba1:
        st.subheader("📄 Organização de Páginas (Primeira e Última)")
        p_primeira, p_ultima = engine.obter_primeira_e_ultima_pagina()
        
        col1, col2 = st.columns(2)
        with col1:
            if p_primeira:
                st.markdown(f"**Página Inicial (Nº {p_primeira.numero})**")
                st.write(f"Primeiros registros: {p_primeira.registros[:5]}")
        with col2:
            if p_ultima:
                st.markdown(f"**Página Final (Nº {p_ultima.numero})**")
                st.write(f"Primeiros registros: {p_ultima.registros[:5]}")

        st.markdown("---")
        st.metric("Total de Registros (NR)", engine.total_registros)
        st.metric("Total de Páginas", len(engine.paginas))
        st.metric("Total de Buckets (NB)", hash_idx.nb)

    with aba2:
        st.subheader("🪣 Visualização dos Buckets")
        st.markdown("Acompanhe o preenchimento de cada bucket e identifique visualmente quais sofreram colisão/overflow.")

        highlight_bucket = st.session_state.ultimo_bucket_buscado

        show_n = st.slider("Buckets a exibir", 8, min(200, hash_idx.nb), min(40, hash_idx.nb), step=8)

        bucket_html = "<div class='bucket-grid'>"
        for b in hash_idx.buckets[:show_n]:
            pct = len(b.entries) / b.capacity * 100 if b.capacity else 0
            is_overflow = bool(b.overflow_chain)
            is_hl = (b.id == highlight_bucket)
            css_cls = "bucket-card"
            if is_hl: 
                css_cls += " highlighted"
            elif is_overflow: 
                css_cls += " overflow"

            fill_color = "#ef4444" if is_overflow else ("#7c6af7" if is_hl else "#4ecdc4")
            
            entries_html = "".join(
                f"<div class='bucket-entry'>{k[:20]} → p{pid}</div>"
                for k, pid in b.entries[:3]
            )
            if len(b.entries) > 3:
                entries_html += f"<div style='color:#4a5568;font-size:0.65rem'>+{len(b.entries)-3} mais</div>"
                
            ov_badge = f"<span style='color:#ef4444;font-size:0.65rem'> ⚡ overflow</span>" if is_overflow else ""
            hl_badge = f"<span style='color:#7c6af7;font-size:0.65rem'> ◀ hash hit</span>" if is_hl else ""

            bucket_html += f"""
            <div class='{css_cls}'>
              <div class='bucket-id'>bucket #{b.id}{ov_badge}{hl_badge}</div>
              {entries_html if b.entries else "<div style='color:#374151;font-size:0.7rem'>vazio</div>"}
              <div class='bucket-fill'>
                <div class='bucket-fill-bar' style='width:{min(pct,100):.0f}%;background:{fill_color}'></div>
              </div>
              <div style='font-size:0.62rem;color:#374151;margin-top:2px'>{len(b.entries)}/{b.capacity} entradas</div>
            </div>"""
            
        bucket_html += "</div>"
        st.markdown(bucket_html, unsafe_allow_html=True)

    with aba3:
        st.subheader("🔎 Pesquisa de Chaves")
        chave_busca = st.text_input("Digite a palavra (chave) que deseja buscar:")
        
        if st.button("Executar Busca"):
            if not chave_busca:
                st.error("Digite uma chave válida.")
            else:
                inicio_idx = time.perf_counter()
                bucket_id = hash_idx.funcao_hash_propria(chave_busca)
                bucket_alvo = hash_idx.buckets[bucket_id]
                
                st.session_state.ultimo_bucket_buscado = bucket_id

                encontrada = False
                pagina_encontrada = None
                pages_read_idx = 0  
                
                current = bucket_alvo
                while current:
                    pages_read_idx += 1  
                    for k, pid in current.entries:
                        if k.lower() == chave_busca.lower():
                            encontrada = True
                            pagina_encontrada = pid
                            break
                    if encontrada:
                        break
                    if current.overflow_chain:
                        current = hash_idx._get_overflow(current.overflow_chain[0])
                    else:
                        break

                tempo_idx = time.perf_counter() - inicio_idx
                
                # Custo do índice retorna estritamente 1 se encontrado, conforme alinhado
                custo_idx = 1 if encontrada else pages_read_idx + 1

                inicio_scan = time.perf_counter()
                scan_encontrado = False
                pagina_scan = None
                
                for pag in engine.paginas:
                    if chave_busca in pag.registros:
                        scan_encontrado = True
                        pagina_scan = pag.numero
                        break
                
                tempo_scan = time.perf_counter() - inicio_scan
                custo_scan = pagina_scan if pagina_scan else len(engine.paginas)

                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.markdown("### Busca por Índice Hash")
                    if encontrada:
                        st.success(f"Chave encontrada!")
                        st.write(f"📁 **Página:** {pagina_encontrada}")
                        st.write(f"🪣 **Bucket:** {bucket_id}")
                        st.write(f"⏱️ **Tempo:** {tempo_idx:.7f} seg")
                        st.write(f"📊 **Custo (Leituras):** {custo_idx} página(s)")
                    else:
                        st.error("Chave não encontrada pelo índice.")

                with res_col2:
                    st.markdown("### Table Scan (Sequencial)")
                    if scan_encontrado:
                        st.warning(f"Chave encontrada via varredura!")
                        st.write(f"📁 **Página:** {pagina_scan}")
                        st.write(f"⏱️ **Tempo:** {tempo_scan:.7f} seg")
                        st.write(f"📊 **Custo (Leituras):** {custo_scan} página(s)")
                    else:
                        st.error("Chave não encontrada.")

                if encontrada and scan_encontrado:
                    st.markdown("---")
                    
                    # Cálculos de ganho percentual
                    economia_paginas = ((custo_scan - custo_idx) / custo_scan) * 100 if custo_scan > 0 else 0
                    
                    if tempo_idx > 0 and tempo_scan > 0:
                        if tempo_idx < tempo_scan:
                            ganho_tempo = ((tempo_scan - tempo_idx) / tempo_scan) * 100
                            texto_tempo = f"O Índice Hash foi **{ganho_tempo:.1f}% mais rápido** em tempo de execução."
                        else:
                            ganho_tempo = ((tempo_idx - tempo_scan) / tempo_idx) * 100
                            texto_tempo = f"O Table Scan foi {ganho_tempo:.1f}% mais rápido nesta execução."
                    else:
                        texto_tempo = "Tempos muito próximos para cálculo percentual."

                    st.info(
                        f"💡 **Comparativo de Desempenho:**\n\n"
                        f"- **Custo de Leitura:** O Índice Hash utilizou **{custo_idx} página** contra **{custo_scan} páginas** do Table Scan. "
                        f"Isso representa uma economia de **{economia_paginas:.1f}% menos acessos a disco**!\n"
                        f"- **Tempo:** {texto_tempo}"
                    )

    with aba4:
        st.markdown("📈 **Métricas e Estatísticas do Índice**")
        
        taxa_col = Metrics.calcular_taxa_colisoes(engine.total_registros, hash_idx.colisoes)
        taxa_over = Metrics.calcular_taxa_overflows(hash_idx.nb, hash_idx.overflows)
        
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("Taxa de Colisões", f"{taxa_col:.2f}%", f"{hash_idx.colisoes} colisões")
        with mcol2:
            st.metric("Taxa de Overflows", f"{taxa_over:.2f}%", f"{hash_idx.overflows} overflows")
        
        st.markdown(f"**Tempo de Construção Inicial do Índice:** `{st.session_state.tempo_construcao:.4f} segundos`")