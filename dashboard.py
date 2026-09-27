import streamlit as st
import pandas as pd
import plotly.express as px
import math

# Configuração da página
st.set_page_config(page_title="Dashboard de Lideranças e Bairros", layout="wide")

# CSS Customizado: Compactação para Mobile e Margens para PC
st.markdown("""
<style>
    /* Container centralizado para dar boas margens no PC e ocupar total no Mobile */
    .main .block-container {
        max-width: 780px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.5rem !important;
    }
    
    /* Card Compacto para Líderes (Caber de 8 a 10 por tela no celular) */
    .lider-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 6px 12px;
        margin-bottom: 6px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
        border: 1px solid #f0f2f6;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .lider-info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .lider-rank {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background-color: #f0f4f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 13px;
        color: #333;
    }

    .lider-nome {
        font-weight: 700;
        font-size: 14px;
        color: #1a1a1a;
        margin: 0;
    }
    
    .lider-stats {
        text-align: right;
    }
    
    .lider-val {
        font-weight: 800;
        font-size: 14px;
        color: #1a1a1a;
    }
    
    .lider-sub {
        font-size: 10px;
        color: #777;
    }

    /* Barra de progresso customizada compacta */
    .progress-bar-bg {
        background-color: #e9ecef;
        border-radius: 4px;
        height: 6px;
        width: 110px;
        margin-top: 3px;
        overflow: hidden;
    }
    .progress-bar-fill {
        background-color: #2b6cb0;
        height: 100%;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- DADOS DE EXEMPLO (Substitua pela sua consulta/dataframe real) ---
@st.cache_data
def load_data():
    # Simulação de 150 líderes
    lideres_data = [
        {"nome": f"Líder {i}", "cadastrados": max(1, 20 - (i // 8)), "meta": 15}
        for i in range(1, 151)
    ]
    # Nomes reais nos primeiros para demonstrar
    lideres_data[0]["nome"] = "Luis Felipe"
    lideres_data[1]["nome"] = "Diego"
    lideres_data[2]["nome"] = "Lucas"
    lideres_data[3]["nome"] = "Tiago"
    
    # Simulação de 50 bairros
    bairros_data = [
        {"bairro": "Outeiro", "apoiadores": 12, "lideres": 3, "veiculos": 2},
        {"bairro": "Boa Perna", "apoiadores": 9, "lideres": 2, "veiculos": 1},
        {"bairro": "Jardim São Paulo", "apoiadores": 8, "lideres": 2, "veiculos": 1},
        {"bairro": "Poente", "apoiadores": 8, "lideres": 1, "veiculos": 0},
        {"bairro": "Vila Canaã", "apoiadores": 5, "lideres": 1, "veiculos": 1},
        {"bairro": "Itatiquara", "apoiadores": 4, "lideres": 1, "veiculos": 0},
        {"bairro": "XV de Novembro", "apoiadores": 4, "lideres": 1, "veiculos": 1},
        {"bairro": "Fazendinha", "apoiadores": 3, "lideres": 1, "veiculos": 0},
        {"bairro": "Centro", "apoiadores": 3, "lideres": 1, "veiculos": 0},
        {"bairro": "Iguabinha", "apoiadores": 3, "lideres": 1, "veiculos": 0},
        {"bairro": "Bananeiras", "apoiadores": 2, "lideres": 1, "veiculos": 0},
        {"bairro": "Parati", "apoiadores": 2, "lideres": 1, "veiculos": 0},
        {"bairro": "Areal", "apoiadores": 2, "lideres": 1, "veiculos": 0},
        {"bairro": "Hawai", "apoiadores": 2, "lideres": 1, "veiculos": 0},
        {"bairro": "Coqueiral", "apoiadores": 2, "lideres": 1, "veiculos": 0},
        {"bairro": "Parque Hotel", "apoiadores": 1, "lideres": 1, "veiculos": 0},
        {"bairro": "Rio do Limão", "apoiadores": 1, "lideres": 1, "veiculos": 0},
    ] + [{"bairro": f"Bairro {i}", "apoiadores": 1, "lideres": 1, "veiculos": 0} for i in range(18, 51)]

    return pd.DataFrame(lideres_data), pd.DataFrame(bairros_data)

df_lideres, df_bairros = load_data()

# --- ABA DE NAVEGAÇÃO ---
tab_lideres, tab_bairros = st.tabs(["🏆 Liderança", "📍 Bairros"])

# ==========================================
# 1. ABA LIDERANÇA
# ==========================================
with tab_lideres:
    st.subheader("Leaderboard de Lideranças")
    
    # Ordenação por cadastrados (Decrescente)
    df_lideres_sorted = df_lideres.sort_values(by="cadastrados", ascending=False).reset_index(drop=True)
    
    # Paginação (20 por página)
    ITENS_POR_PAGINA = 20
    total_paginas = math.ceil(len(df_lideres_sorted) / ITENS_POR_PAGINA)
    
    col_pag, col_info = st.columns([2, 1])
    with col_pag:
        pagina_atual = st.selectbox(
            "Página:", 
            options=list(range(1, total_paginas + 1)),
            format_func=lambda x: f"Página {x} de {total_paginas} (Líderes {((x-1)*ITENS_POR_PAGINA)+1} a {min(x*ITENS_POR_PAGINA, len(df_lideres_sorted))})"
        )
    
    idx_inicio = (pagina_atual - 1) * ITENS_POR_PAGINA
    idx_fim = idx_inicio + ITENS_POR_PAGINA
    df_pagina = df_lideres_sorted.iloc[idx_inicio:idx_fim]
    
    # Renderização Compacta dos Cards
    for i, row in df_pagina.iterrows():
        posicao = i + 1
        pct = min(100, int((row['cadastrados'] / row['meta']) * 100))
        faltam = max(0, row['meta'] - row['cadastrados'])
        
        # Ícone do Top 3 ou Posição
        if posicao == 1:
            badge = "🥇"
        elif posicao == 2:
            badge = "🥈"
        elif posicao == 3:
            badge = "🥉"
        else:
            badge = f"{posicao}"

        html_card = f"""
        <div class="lider-card">
            <div class="lider-info">
                <div class="lider-rank">{badge}</div>
                <div>
                    <p class="lider-nome">{row['nome']}</p>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {pct}%;"></div>
                    </div>
                </div>
            </div>
            <div class="lider-stats">
                <div class="lider-val">{row['cadastrados']}/{row['meta']}</div>
                <div class="lider-sub">Faltam {faltam}</div>
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)


# ==========================================
# 2. ABA BAIRROS
# ==========================================
with tab_bairros:
    st.subheader("🔥 Top 15 Bairros")
    
    # Garantir ordem decrescente
    df_bairros_sorted = df_bairros.sort_values(by="apoiadores", ascending=False).reset_index(drop=True)
    
    # Filtrar Top 15 para o Gráfico
    df_top15 = df_bairros_sorted.head(15)
    
    # Gráfico de Barras Top 15
    fig = px.bar(
        df_top15,
        x="bairro",
        y="apoiadores",
        text="apoiadores",
        color_discrete_sequence=["#1f66ad"]
    )
    
    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=80),
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(showticklabels=False, showgrid=False),
        xaxis=dict(tickangle=-90, tickfont=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=280
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    st.subheader("🔍 Explorador de Bairros (Ordem Decrescente)")
    
    # Filtros e Buscas
    bairro_selecionado = st.selectbox("Filtrar visualização", ["Todos os Bairros"] + list(df_bairros_sorted["bairro"].unique()))
    
    df_exibicao = df_bairros_sorted if bairro_selecionado == "Todos os Bairros" else df_bairros_sorted[df_bairros_sorted["bairro"] == bairro_selecionado]
    
    # Listagem de Bairros em Expanders / Cards
    for _, row in df_exibicao.iterrows():
        with st.expander(f"📍 {row['bairro']} — {row['apoiadores']} Apoiador(es)"):
            st.write(f"• **Líderes no bairro:** {row['lideres']}")
            st.write(f"• **Veículos cadastrados:** {row['veiculos']}")
