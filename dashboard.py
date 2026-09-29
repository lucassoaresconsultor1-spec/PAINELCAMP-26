import io
import math
import re
import unicodedata
from datetime import date, datetime
import sys

# Tratamento para zoneinfo (garante compatibilidade no Windows/Linux)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

# =====================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="Campanha 2026 · Centro de Comando",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# 2. IDENTIDADE VISUAL & CSS DESIGN SYSTEM
# =====================================================================
NAVY = "#071A2D"
NAVY_SOFT = "#123A63"
BLUE = "#1D5FA6"
AMBER = "#F0A629"
GREEN = "#2E9E6D"
RED = "#C0392B"
BG = "#F4F6F9"
CARD = "#FFFFFF"
TEXT = "#16202A"
MUTED = "#728096"
BORDER = "#E6EBF2"

PLOTLY_FONT = "Manrope, sans-serif"
SENHA_PADRAO = "Araruama321@"
DATA_ELEICAO = date(2026, 10, 4)
FUSO_SP = ZoneInfo("America/Sao_Paulo")


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', 'Manrope', -apple-system, sans-serif;
            color: {TEXT};
            background-color: {BG};
            -webkit-font-smoothing: antialiased;
        }}

        #MainMenu, footer, header {{ visibility: hidden; height: 0; }}

        .stApp {{
            background:
                radial-gradient(800px circle at 15% -10%, rgba(29, 95, 166, 0.12) 0%, transparent 60%),
                radial-gradient(700px circle at 85% 110%, rgba(240, 166, 41, 0.08) 0%, transparent 50%),
                {BG};
            background-attachment: fixed;
        }}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 3rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 1280px;
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* HERO BANNER RESPONSIVO */
        .hero-banner {{
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_SOFT} 50%, {BLUE} 100%);
            border-radius: 20px;
            padding: 24px 20px;
            color: #FFFFFF;
            margin-bottom: 20px;
            position: relative;
            box-shadow: 0 16px 32px -10px rgba(7, 26, 45, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.12);
            animation: fadeInUp 0.4s ease-out;
        }}
        @media (min-width: 768px) {{
            .hero-banner {{ border-radius: 24px; padding: 32px 36px; margin-bottom: 24px; }}
        }}

        .hero-tag-container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .hero-tag {{
            background: rgba(240, 166, 41, 0.15);
            border: 1px solid rgba(240, 166, 41, 0.4);
            color: {AMBER};
            font-weight: 800;
            font-size: 0.7rem;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 30px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .hero-banner h1 {{
            margin: 0;
            font-size: 1.6rem;
            font-weight: 800;
            line-height: 1.2;
            color: #FFFFFF;
        }}
        @media (min-width: 768px) {{
            .hero-banner h1 {{ font-size: 2.2rem; }}
        }}

        .countdown-box {{
            margin-top: 14px;
            background: rgba(240, 166, 41, 0.15);
            border: 1px solid rgba(240, 166, 41, 0.4);
            border-radius: 14px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .countdown-text {{
            font-size: 1.05rem;
            font-weight: 800;
            color: {AMBER};
        }}

        /* GRID DE KPIS */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 18px;
        }}
        @media (min-width: 900px) {{
            .kpi-grid {{ grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 22px; }}
        }}

        .kpi-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 14px 16px;
            position: relative;
            box-shadow: 0 4px 14px rgba(7, 26, 45, 0.03);
        }}
        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, {NAVY} 0%, {BLUE} 100%);
        }}
        .kpi-card .kpi-label {{
            color: {MUTED};
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .kpi-card .kpi-value {{
            color: {NAVY};
            font-size: 1.7rem;
            font-weight: 800;
            margin-top: 2px;
        }}
        .kpi-card.kpi-alert::before {{
            background: linear-gradient(90deg, {RED} 0%, {AMBER} 100%);
        }}

        /* SEÇÃO CARD */
        .section-card {{
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px rgba(7, 26, 45, 0.04);
        }}
        @media (min-width: 768px) {{
            .section-card {{ border-radius: 20px; padding: 24px 28px; margin-bottom: 22px; }}
        }}

        .section-header-wrap {{
            border-bottom: 1px solid {BORDER};
            padding-bottom: 10px;
            margin-bottom: 16px;
        }}
        .section-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: {NAVY};
        }}
        .section-subtitle {{
            color: {MUTED};
            font-size: 0.82rem;
            font-weight: 500;
        }}

        /* CARD COMPACTO PARA LEADERBOARD */
        .lider-card-compact {{
            background: #FFFFFF;
            border-radius: 14px;
            padding: 10px 14px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            border: 1px solid #E2E8F0;
            margin-bottom: 8px;
        }}

        .rank-badge {{
            background: #FEF3D6;
            color: #B47818;
            border-radius: 8px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.9rem;
            flex-shrink: 0;
        }}

        .custom-card {{
            background: #FFFFFF;
            border-radius: 16px;
            padding: 12px 14px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            border: 1px solid #E2E8F0;
            margin-bottom: 10px;
        }}

        /* CARD DE GRUPO DUPLICADO */
        .dup-card {{
            background: #FFFFFF;
            border-radius: 14px;
            padding: 10px 14px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            border: 1px solid #F3D6D2;
            border-left: 5px solid {RED};
            margin-bottom: 8px;
        }}
        .dup-title {{
            font-weight: 800;
            font-size: 0.95rem;
            color: {NAVY};
        }}
        .dup-sub {{
            font-size: 0.75rem;
            color: {MUTED};
            font-weight: 600;
            margin-top: 2px;
        }}

        /* CARD COMPACTO DE VEÍCULOS */
        .vehicle-card {{
            background: #FFFFFF;
            border-radius: 14px;
            padding: 10px 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            border: 1px solid #E2E8F0;
            margin-bottom: 8px;
        }}

        .vehicle-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}

        .vehicle-title {{
            font-weight: 800;
            font-size: 0.9rem;
            color: {NAVY};
            line-height: 1.2;
        }}

        .vehicle-sub {{
            font-size: 0.75rem;
            color: {MUTED};
            font-weight: 600;
            margin-top: 2px;
        }}

        /* LINHA DE EMBLEMAS/CHIPS COMPACTA E OBRIGATORIAMENTE EM 1 LINHA */
        .chips-inline-container {{
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            align-items: center;
            gap: 6px;
            margin-top: 8px;
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .chips-inline-container::-webkit-scrollbar {{
            display: none;
        }}

        .chip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 14px;
            font-size: 0.7rem;
            font-weight: 700;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .chip-blue {{ background: #EBF3FA; color: {BLUE}; border: 1px solid rgba(29, 95, 166, 0.15); }}
        .chip-amber {{ background: #FEF3D6; color: #B47818; border: 1px solid rgba(240, 166, 41, 0.25); }}
        .chip-green {{ background: #E8F5E9; color: {GREEN}; border: 1px solid rgba(46, 158, 109, 0.2); }}
        .chip-red {{ background: #FDECEA; color: {RED}; border: 1px solid rgba(192, 57, 43, 0.25); }}
        .chip-muted {{ background: #F1F5F9; color: {MUTED}; border: 1px solid {BORDER}; }}

        /* PROGRESS BAR CUSTOMIZADA COMPACTA */
        .custom-progress-bg {{
            background-color: #E2E8F0;
            border-radius: 6px;
            height: 6px;
            width: 100%;
            overflow: hidden;
        }}
        .custom-progress-fill {{
            background-color: {BLUE};
            height: 100%;
            border-radius: 6px;
        }}

        /* FICHA DO APOIADOR */
        .person-card {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 8px;
            background: {CARD};
        }}
        .person-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}
        .person-name {{ font-weight: 800; color: {NAVY}; font-size: 0.9rem; }}
        .wa-link {{
            text-decoration: none !important;
            background: linear-gradient(135deg, {GREEN} 0%, #227C55 100%);
            color: #FFFFFF !important;
            font-size: 0.7rem;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .ficha-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            margin-top: 8px;
        }}
        @media (min-width: 640px) {{
            .ficha-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .ficha-item {{
            background: #F8FAFC;
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 8px 12px;
        }}
        .ficha-label {{
            font-size: 0.68rem;
            font-weight: 800;
            color: {MUTED};
            text-transform: uppercase;
        }}
        .ficha-value {{ font-size: 0.86rem; font-weight: 700; color: {NAVY}; margin-top: 2px; }}

        /* TELA DE LOGIN */
        .login-card {{
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(244, 246, 249, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 24px;
            padding: 36px 24px;
            max-width: 420px;
            margin: 40px auto 0 auto;
            text-align: center;
            box-shadow: 0 20px 50px rgba(7, 26, 45, 0.12);
        }}
        .login-icon {{
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, {NAVY} 0%, {BLUE} 100%);
            color: {AMBER};
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            margin-bottom: 16px;
        }}

        div[data-testid="stButton"] button {{
            background: linear-gradient(135deg, {NAVY} 0%, {BLUE} 100%);
            color: white;
            border: none;
            font-weight: 700;
            border-radius: 12px;
            padding: 10px 18px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================
# 3. FUNÇÃO DE LIMPEZA DE TEXTO (CORREÇÃO DE DIGITAÇÃO E ACENTOS)
# =====================================================================
def limpar_texto(texto):
    """
    Remove acentos, caracteres especiais extras, múltiplos espaços
    e padroniza tudo em maiúsculas para agrupar erros de digitação semelhantes.
    Exemplo: 'Rio Do limao ' -> 'RIO DO LIMAO'
             'Rio do Limão' -> 'RIO DO LIMAO'
    """
    if pd.isna(texto) or not str(texto).strip():
        return ""
    txt = str(texto).strip().upper()
    if txt in ["NAN", "NONE", "NAO", "NÃO", "NAO POSSUI", "NÃO POSSUI", "NENHUM", "NEHUM", "0", "-", "NÃO INFORMADO"]:
        return ""
    # Remove acentuação
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    # Substitui múltiplos espaços por um único espaço
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()


def safe_title(text):
    if pd.isna(text) or text is None:
        return ""
    txt = str(text).strip()
    if txt.upper() in ["NAN", "NONE", "NAO", "NÃO", "NAO POSSUI", "NÃO POSSUI", "NENHUM", "NEHUM", "", "0", "-", "NÃO INFORMADO"]:
        return ""
    return txt.title()


def normalizar(col: str) -> str:
    return (
        col.upper()
        .replace("Ç", "C")
        .replace("Ã", "A")
        .replace("Á", "A")
        .replace("Â", "A")
        .replace("Õ", "O")
        .replace("Ó", "O")
        .replace("É", "E")
        .replace("Ê", "E")
        .replace("Í", "I")
        .replace("Ú", "U")
        .strip()
    )


def mask_cpf(cpf: str) -> str:
    digitos = re.sub(r"\D", "", str(cpf))
    if len(digitos) < 4:
        return "***.***.***-**"
    return f"***.***.**{digitos[-4:-2]}-{digitos[-2:]}"


def mask_titulo(titulo: str) -> str:
    digitos = re.sub(r"\D", "", str(titulo))
    if len(digitos) < 4:
        return "**** **** ****"
    return f"**** **** **{digitos[-2:]}"


def whatsapp_link(contato: str) -> str:
    if not contato:
        return ""
    digitos = re.sub(r"\D", "", str(contato))
    if len(digitos) < 10:
        return str(contato)
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    return f'<a class="wa-link" href="https://wa.me/{digitos}" target="_blank">💬 WhatsApp</a>'


# =====================================================================
# 3.1 FUNÇÕES DE DOCUMENTOS (CPF / TÍTULO) PARA DETECÇÃO DE DUPLICATAS
# =====================================================================
def normalizar_documento(valor, tamanho: int) -> str:
    """
    Retorna apenas os dígitos do documento (CPF=11, Título=12).
    - Remove pontos, traços e espaços.
    - Remove o '.0' que o pandas cria quando lê número como float.
    - Recompõe zeros à esquerda perdidos na planilha.
    - Retorna '' quando o campo está vazio ou inválido (ex.: só zeros).
    """
    if valor is None or pd.isna(valor):
        return ""
    txt = str(valor).strip()
    txt = re.sub(r"\.0+$", "", txt)
    digitos = re.sub(r"\D", "", txt)
    if not digitos or set(digitos) == {"0"}:
        return ""
    if len(digitos) < tamanho:
        digitos = digitos.zfill(tamanho)
    return digitos


def formatar_cpf(digitos: str) -> str:
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return digitos


def formatar_titulo(digitos: str) -> str:
    if len(digitos) == 12:
        return f"{digitos[:4]} {digitos[4:8]} {digitos[8:]}"
    return digitos


# =====================================================================
# 4. CARREGAMENTO DOS DADOS (COM HIGIENIZAÇÃO DE TEXTO INTEGRADA)
# =====================================================================
URL_SHEETS = "https://docs.google.com/spreadsheets/d/17FGnNHegZTxubuE2B3bGNQcgiTT8i8EpqD6rOdmItVM/export?format=csv"


@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(URL_SHEETS)
    df.columns = df.columns.astype(str).str.strip()

    def buscar_coluna(termos_busca, excluir=None):
        excluir = excluir or []
        for col in df.columns:
            col_clean = normalizar(col)
            if any(ex in col_clean for ex in excluir):
                continue
            for termo in termos_busca:
                if termo in col_clean:
                    return col
        return None

    col_timestamp = buscar_coluna(["CARIMBO"])
    col_lider = buscar_coluna(["LIDER", "INDICACAO"])
    col_nome = buscar_coluna(["NOME"], excluir=["MAE"])
    col_contato = buscar_coluna(["CONTATO", "TELEFONE", "CELULAR", "ZAP", "WHATSAPP"])
    col_nasc = buscar_coluna(["NASCIMENTO"])
    col_mae = buscar_coluna(["MAE"])
    col_titulo = buscar_coluna(["TITULO"])
    col_cpf = buscar_coluna(["CPF"])
    col_local_votacao = buscar_coluna(["LOCAL DE VOTACAO", "LOCAL VOTACAO", "SECAO", "COLEGIO"])
    col_bairro = buscar_coluna(["BAIRRO"])
    col_veiculo = buscar_coluna(["VEICULO", "MODELO"])

    renomear = {}
    if col_timestamp:
        renomear[col_timestamp] = "TIMESTAMP_PADRAO"
    if col_lider:
        renomear[col_lider] = "LIDER_PADRAO"
    if col_nome:
        renomear[col_nome] = "NOME_PADRAO"
    if col_contato:
        renomear[col_contato] = "CONTATO_PADRAO"
    if col_nasc:
        renomear[col_nasc] = "NASCIMENTO_PADRAO"
    if col_mae:
        renomear[col_mae] = "MAE_PADRAO"
    if col_titulo:
        renomear[col_titulo] = "TITULO_PADRAO"
    if col_cpf:
        renomear[col_cpf] = "CPF_PADRAO"
    if col_local_votacao:
        renomear[col_local_votacao] = "LOCAL_VOTACAO_PADRAO"
    if col_bairro:
        renomear[col_bairro] = "BAIRRO_PADRAO"
    if col_veiculo:
        renomear[col_veiculo] = "VEICULO_INFO_PADRAO"

    df = df.rename(columns=renomear)

    # APLICA A HIGIENIZAÇÃO/PADRONIZAÇÃO DE DIGITAÇÃO NAS COLUNAS DE TEXTO
    for c in ["LIDER_PADRAO", "BAIRRO_PADRAO", "VEICULO_INFO_PADRAO"]:
        if c in df.columns:
            df[c] = df[c].apply(limpar_texto)

    for c in ["NOME_PADRAO", "MAE_PADRAO", "LOCAL_VOTACAO_PADRAO", "CONTATO_PADRAO", "TITULO_PADRAO", "CPF_PADRAO"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    if "TIMESTAMP_PADRAO" in df.columns:
        df["Timestamp_DT"] = pd.to_datetime(df["TIMESTAMP_PADRAO"], dayfirst=True, errors="coerce")

    hoje_data_sp = datetime.now(FUSO_SP).date()
    if "NASCIMENTO_PADRAO" in df.columns:
        df["Data_Nasc_DT"] = pd.to_datetime(df["NASCIMENTO_PADRAO"], dayfirst=True, errors="coerce")

        def calcular_idade(nasc):
            if pd.isna(nasc):
                return np.nan
            nasc = nasc.date()
            idade = hoje_data_sp.year - nasc.year - ((hoje_data_sp.month, hoje_data_sp.day) < (nasc.month, nasc.day))
            return idade if 0 <= idade <= 120 else np.nan

        df["Idade"] = df["Data_Nasc_DT"].apply(calcular_idade)

        def classificar_faixa(idade):
            if pd.isna(idade):
                return "Não informado"
            elif idade < 25:
                return "18-24 anos"
            elif idade < 40:
                return "25-39 anos"
            elif idade < 60:
                return "40-59 anos"
            else:
                return "60+ anos"

        df["Faixa_Etaria"] = df["Idade"].apply(classificar_faixa)

    return df


def verificar_senha():
    senha_correta = st.secrets.get("senha_acesso", SENHA_PADRAO)
    if st.session_state.get("autenticado"):
        return

    st.markdown(
        f"""
        <div class="login-card">
            <div class="login-icon">🗳️</div>
            <div style="color:{AMBER}; font-weight:800; font-size:0.75rem; letter-spacing:1.5px; text-transform:uppercase;">ACESSO EXCLUSIVO</div>
            <h1 style="font-size:1.6rem; font-weight:800; color:{NAVY}; margin:10px 0 6px 0;">Campanha 2026</h1>
            <p style="color:{MUTED}; font-size:0.88rem; margin-bottom:24px;">Insira a senha credenciada para acessar o sistema.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, col_b, _ = st.columns([0.2, 1.6, 0.2])
    with col_b:
        senha_digitada = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Digite a senha de acesso...")
        if st.button("Acessar Painel", use_container_width=True):
            if senha_digitada == senha_correta:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()


def parse_veiculo(info: str):
    partes = [p.strip() for p in str(info).split(",") if p.strip()]
    resultado = {"modelo": "", "cor": "", "placa": ""}
    campos = ["modelo", "cor", "placa"]
    for i, valor in enumerate(partes[:3]):
        resultado[campos[i]] = valor.title() if campos[i] != "placa" else valor.upper()
    return resultado


def veiculo_valido(valor: str) -> bool:
    if pd.isna(valor):
        return False
    v = str(valor).strip().upper()
    return v not in ["NAN", "NONE", "NAO", "NÃO", "NAO POSSUI", "NÃO POSSUI", "NENHUM", "NEHUM", "", "0", "-"]


# =====================================================================
# RENDERIZAÇÃO DE FICHAS E PESSOAS
# =====================================================================
def render_ficha_completa(r, exibir_dados_sensiveis: bool):
    nasc = r.get("NASCIMENTO_PADRAO", "")
    idade = r.get("Idade", np.nan)
    idade_txt = f"{int(idade)} anos" if pd.notna(idade) else "—"
    mae = safe_title(r.get("MAE_PADRAO", "")) or "—"

    titulo_raw = str(r.get("TITULO_PADRAO", "")).strip()
    if not titulo_raw or titulo_raw.upper() in ["NAN", "NONE", "NAO", "NÃO", "0", "-"]:
        titulo_txt = "—"
    else:
        titulo_txt = titulo_raw if exibir_dados_sensiveis else mask_titulo(titulo_raw)

    cpf_raw = str(r.get("CPF_PADRAO", "")).strip()
    if not cpf_raw or cpf_raw.upper() in ["NAN", "NONE", "NAO", "NÃO", "0", "-"]:
        cpf_txt = "—"
    else:
        cpf_txt = cpf_raw if exibir_dados_sensiveis else mask_cpf(cpf_raw)

    local_votacao = safe_title(r.get("LOCAL_VOTACAO_PADRAO", "")) or "—"

    st.markdown(
        f"""
        <div class="ficha-grid">
            <div class="ficha-item"><div class="ficha-label">Data de Nascimento</div><div class="ficha-value">{nasc or "—"} ({idade_txt})</div></div>
            <div class="ficha-item"><div class="ficha-label">Nome da Mãe</div><div class="ficha-value">{mae}</div></div>
            <div class="ficha-item"><div class="ficha-label">Título de Eleitor</div><div class="ficha-value">{titulo_txt}</div></div>
            <div class="ficha-item"><div class="ficha-label">CPF</div><div class="ficha-value">{cpf_txt}</div></div>
            <div class="ficha-item" style="grid-column: 1 / -1;"><div class="ficha-label">Local de Votação</div><div class="ficha-value">{local_votacao}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_person_card(r, exibir_dados_sensiveis: bool):
    nome = safe_title(r.get("NOME_PADRAO", "—")) or "—"
    bairro = safe_title(r.get("BAIRRO_PADRAO", ""))
    lider = safe_title(r.get("LIDER_PADRAO", ""))
    contato = r.get("CONTATO_PADRAO", "") if "CONTATO_PADRAO" in r else ""
    wa = whatsapp_link(contato)

    chips = ""
    if bairro:
        chips += f'<span class="chip chip-muted">📍 {bairro}</span> '
    if lider:
        chips += f'<span class="chip chip-blue">⭐ Líder: {lider}</span>'

    st.markdown(
        f"""
        <div class="person-card">
            <div class="person-top">
                <div>
                    <div class="person-name">{nome}</div>
                    <div style="margin-top:4px;">{chips}</div>
                </div>
                {wa}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("🔎 Ver ficha completa"):
        render_ficha_completa(r, exibir_dados_sensiveis)


# =====================================================================
# INTERFACE PRINCIPAL
# =====================================================================
inject_css()
verificar_senha()

df = carregar_dados()

if "VEICULO_INFO_PADRAO" in df.columns:
    df_veiculos_filtro = df[df["VEICULO_INFO_PADRAO"].apply(veiculo_valido)].copy()
else:
    df_veiculos_filtro = pd.DataFrame()

total_cadastros = len(df)
lideres_ativos = df["LIDER_PADRAO"].replace("", np.nan).dropna().nunique() if "LIDER_PADRAO" in df.columns else 0
bairros_cobertos = df["BAIRRO_PADRAO"].replace("", np.nan).dropna().nunique() if "BAIRRO_PADRAO" in df.columns else 0
veiculos_mapeados = len(df_veiculos_filtro)

hoje_sp = datetime.now(FUSO_SP)
hoje_data = hoje_sp.date()
dias_restantes = (DATA_ELEICAO - hoje_data).days

if dias_restantes > 1:
    texto_dias = f"Faltam <b>{dias_restantes} dias</b> para as eleições."
elif dias_restantes == 1:
    texto_dias = "Falta <b>1 dia</b> para as eleições!"
else:
    texto_dias = "É HOJE! Dia da Eleição! 🗳️"

agora = hoje_sp.strftime("%d/%m/%Y às %H:%M")

# HERO BANNER
st.markdown(
    f"""<div class="hero-banner">
        <div class="hero-tag-container">
            <div class="hero-tag">🗳️ CENTRO DE COMANDO 2026</div>
            <div style="font-size:0.75rem; color:#CBD5E1; font-weight:600;">🔄 {agora}</div>
        </div>
        <h1>Painel de Operações</h1>
        <p>Monitoramento estratégico de mobilização e base em tempo real.</p>
        <div class="countdown-box">
            <div style="font-size:1.5rem;">⏳</div>
            <div>
                <div style="font-size:0.7rem; font-weight:800; color:#FCE7F3; text-transform:uppercase;">Contagem Regressiva</div>
                <div class="countdown-text">{texto_dias}</div>
            </div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

# KPIS
st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-label">Cadastros</div><div class="kpi-value">{total_cadastros}</div></div>
        <div class="kpi-card"><div class="kpi-label">Líderes</div><div class="kpi-value">{lideres_ativos}</div></div>
        <div class="kpi-card"><div class="kpi-label">Bairros</div><div class="kpi-value">{bairros_cobertos}</div></div>
        <div class="kpi-card"><div class="kpi-label">Veículos</div><div class="kpi-value">{veiculos_mapeados}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# CONTROLE DE DADOS SENSÍVEIS (CPF E TÍTULO)
col_toggle, _ = st.columns([1, 2])
with col_toggle:
    exibir_dados_sensiveis = st.checkbox("🔓 Exibir CPF e Título de Eleitor completos", value=False)

# NAVEGAÇÃO
selected = option_menu(
    menu_title=None,
    options=["Liderança", "Bairros", "Veículos", "Perfil Demográfico", "Duplicatas", "Relatórios"],
    icons=["people-fill", "geo-alt-fill", "car-front-fill", "bar-chart-fill", "exclamation-triangle-fill", "download"],
    orientation="horizontal",
    styles={
        "container": {"padding": "4px", "background-color": CARD, "border": f"1px solid {BORDER}", "border-radius": "14px", "margin-bottom": "18px"},
        "icon": {"color": MUTED, "font-size": "13px"},
        "nav-link": {"font-family": "Plus Jakarta Sans, sans-serif", "font-weight": "700", "font-size": "0.78rem", "color": MUTED, "text-align": "center", "border-radius": "10px", "padding": "8px 6px"},
        "nav-link-selected": {"background-color": NAVY, "color": "#FFFFFF"},
    },
)

# ==========================================
# ABA 1: LIDERANÇA
# ==========================================
if selected == "Liderança":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">🏆 Leaderboard de Lideranças</div>
            <div class="section-subtitle">Acompanhe os cadastros por liderança em ordem de desempenho.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if "LIDER_PADRAO" in df.columns and not df.empty:
        df_clean_lider = df[df["LIDER_PADRAO"] != ""]

        col_search_lider, col_pag = st.columns([1, 1])
        with col_search_lider:
            busca_lider = st.text_input("Buscar líder pelo nome", placeholder="Digite o nome do líder...")

        df_lideres = (
            df_clean_lider["LIDER_PADRAO"].value_counts().reset_index()
            .rename(columns={"LIDER_PADRAO": "Líder", "count": "Total"})
            .sort_values(by="Total", ascending=False)
            .reset_index(drop=True)
        )

        if busca_lider:
            df_lideres = df_lideres[df_lideres["Líder"].str.contains(busca_lider.upper(), na=False)].reset_index(drop=True)

        ITENS_POR_PAGINA = 20
        total_lideres = len(df_lideres)
        total_paginas = math.ceil(total_lideres / ITENS_POR_PAGINA) if total_lideres > 0 else 1

        with col_pag:
            if total_lideres > 0:
                pagina_atual = st.selectbox(
                    "Navegação de Páginas:",
                    options=list(range(1, total_paginas + 1)),
                    format_func=lambda x: f"Página {x} de {total_paginas} ({((x-1)*ITENS_POR_PAGINA)+1} a {min(x*ITENS_POR_PAGINA, total_lideres)} de {total_lideres} líderes)"
                )
            else:
                pagina_atual = 1

        if total_lideres > 0:
            idx_inicio = (pagina_atual - 1) * ITENS_POR_PAGINA
            idx_fim = idx_inicio + ITENS_POR_PAGINA
            df_pagina_lideres = df_lideres.iloc[idx_inicio:idx_fim]

            for i, row in df_pagina_lideres.iterrows():
                posicao = idx_inicio + i + 1
                lider_nome = safe_title(row['Líder'])
                total_ind = row['Total']
                pct = (total_ind / total_cadastros * 100) if total_cadastros else 0

                if posicao == 1:
                    badge = "🥇"
                elif posicao == 2:
                    badge = "🥈"
                elif posicao == 3:
                    badge = "🥉"
                else:
                    badge = f"{posicao}"

                st.markdown(
                    f"""
                    <div class="lider-card-compact">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="rank-badge">{badge}</div>
                                <div>
                                    <div style="font-size: 0.95rem; font-weight: 800; color: #071A2D;">{lider_nome}</div>
                                    <div style="font-size: 0.75rem; font-weight: 600; color: #728096;">{pct:.1f}% da base total</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.25rem; font-weight: 800; color: #071A2D;">{total_ind}</div>
                                <div style="font-size: 0.68rem; font-weight: 700; color: #728096; text-transform: uppercase;">Indicados</div>
                            </div>
                        </div>
                        <div class="custom-progress-bg" style="margin-top: 8px;">
                            <div class="custom-progress-fill" style="width: {min(100, pct*2)}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"👥 Ver {total_ind} pessoas indicadas por {lider_nome}"):
                    indicados = df_clean_lider[df_clean_lider["LIDER_PADRAO"] == row['Líder']]
                    for _, r in indicados.iterrows():
                        render_person_card(r, exibir_dados_sensiveis)
        else:
            st.info("Nenhuma liderança encontrada com os filtros aplicados.")

    else:
        st.info("Nenhum dado de liderança encontrado na planilha.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 2: BAIRROS (DADOS TOTALMENTE SANITIZADOS)
# ==========================================
if selected == "Bairros":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">📍 Cobertura por Bairro</div>
            <div class="section-subtitle">Visualização gráfica e lista completa por volume de apoiadores.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if "BAIRRO_PADRAO" in df.columns:
        df_bairros_validos = df[df["BAIRRO_PADRAO"] != ""]

        bairros_summary = (
            df_bairros_validos.groupby("BAIRRO_PADRAO")
            .agg(
                Total_Apoiadores=("BAIRRO_PADRAO", "count"),
                Lideres_Distintos=("LIDER_PADRAO", lambda x: len(set(x.replace("", np.nan).dropna()))),
                Veiculos=("VEICULO_INFO_PADRAO", lambda x: len([v for v in x if veiculo_valido(v)])),
            )
            .reset_index()
            .sort_values(by="Total_Apoiadores", ascending=False)
            .reset_index(drop=True)
        )

        st.markdown("<h4 style='font-size:0.95rem; font-weight:800; color:#071A2D; margin-bottom:10px;'>🔥 Top 15 Bairros com Mais Apoiadores</h4>", unsafe_allow_html=True)
        df_top15 = bairros_summary.head(15).copy()
        df_top15["Bairro_Fmt"] = df_top15["BAIRRO_PADRAO"].apply(safe_title)

        fig_top15 = px.bar(
            df_top15,
            x="Bairro_Fmt",
            y="Total_Apoiadores",
            text="Total_Apoiadores",
            color_discrete_sequence=[BLUE]
        )
        fig_top15.update_traces(
            textposition="outside",
            cliponaxis=False
        )
        fig_top15.update_layout(
            font_family=PLOTLY_FONT,
            font_color=TEXT,
            margin=dict(l=10, r=10, t=20, b=80),
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(showticklabels=False, showgrid=False),
            xaxis=dict(tickangle=-90, tickfont=dict(size=11, weight="bold")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=280
        )
        st.plotly_chart(fig_top15, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E6EBF2;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:0.95rem; font-weight:800; color:#071A2D; margin-bottom:12px;'>🔍 Lista Detalhada de Bairros (Ordem Decrescente)</h4>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            lista_bairros_select = ["Todos os Bairros"] + [safe_title(b) for b in bairros_summary["BAIRRO_PADRAO"]]
            bairro_sel = st.selectbox("Filtrar por bairro", lista_bairros_select)
        with col_f2:
            busca_nome = st.text_input("Buscar morador por nome", placeholder="Digite para filtrar...")

        if bairro_sel != "Todos os Bairros":
            bairros_para_exibir = [b for b in bairros_summary["BAIRRO_PADRAO"] if safe_title(b) == bairro_sel]
        else:
            bairros_para_exibir = list(bairros_summary["BAIRRO_PADRAO"])

        for b in bairros_para_exibir:
            sub_df = df_bairros_validos[df_bairros_validos["BAIRRO_PADRAO"] == b]
            if busca_nome:
                sub_df = sub_df[sub_df["NOME_PADRAO"].str.upper().str.contains(busca_nome.upper(), na=False)]
            if sub_df.empty:
                continue

            info_bairro = bairros_summary[bairros_summary["BAIRRO_PADRAO"] == b]
            vol_apoiadores = info_bairro["Total_Apoiadores"].values[0] if not info_bairro.empty else len(sub_df)
            vol_lideres = info_bairro["Lideres_Distintos"].values[0] if not info_bairro.empty else 0
            vol_veiculos = info_bairro["Veiculos"].values[0] if not info_bairro.empty else 0

            st.markdown(
                f"""
                <div class="custom-card">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #071A2D; display: flex; align-items: center; gap: 6px;">
                        📍 {safe_title(b)}
                    </div>
                    <div class="chips-inline-container">
                        <span class="chip chip-blue">👥 {vol_apoiadores} Apoiador(es)</span>
                        <span class="chip chip-amber">⭐ {vol_lideres} Líder(es)</span>
                        <span class="chip chip-green">🚗 {vol_veiculos} Veículo(s)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"📋 Ver lista de moradores cadastrados em {safe_title(b)}"):
                for _, r in sub_df.iterrows():
                    render_person_card(r, exibir_dados_sensiveis)

    else:
        st.info("Coluna de bairro não encontrada na planilha.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 3: VEÍCULOS
# ==========================================
if selected == "Veículos":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">🚗 Frota Mapeada</div>
            <div class="section-subtitle">Veículos cadastrados para apoio logístico</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if not df_veiculos_filtro.empty:
        c_v1, c_v2 = st.columns([1, 1])
        with c_v1:
            bairros_v_validos = sorted([safe_title(b) for b in df_veiculos_filtro["BAIRRO_PADRAO"].dropna().unique() if b != ""])
            bairro_v_sel = st.selectbox("Filtrar por bairro", ["Todos os bairros"] + bairros_v_validos)
        with c_v2:
            busca_veiculo = st.text_input("Filtrar modelo/motorista", placeholder="Ex: Gol, Fiat...")

        df_veic_exibir = df_veiculos_filtro.copy()
        if bairro_v_sel != "Todos os bairros":
            df_veic_exibir = df_veic_exibir[df_veic_exibir["BAIRRO_PADRAO"].apply(safe_title) == bairro_v_sel]
        if busca_veiculo:
            termo = busca_veiculo.upper()
            df_veic_exibir = df_veic_exibir[
                df_veic_exibir["VEICULO_INFO_PADRAO"].str.upper().str.contains(termo, na=False)
                | df_veic_exibir["NOME_PADRAO"].str.upper().str.contains(termo, na=False)
            ]

        for _, r in df_veic_exibir.iterrows():
            nome = safe_title(r.get("NOME_PADRAO", "—"))
            bairro = safe_title(r.get("BAIRRO_PADRAO", ""))
            lider = safe_title(r.get("LIDER_PADRAO", ""))
            contato = r.get("CONTATO_PADRAO", "") if "CONTATO_PADRAO" in r else ""
            wa = whatsapp_link(contato)

            partes = parse_veiculo(r.get("VEICULO_INFO_PADRAO", ""))
            veiculo_titulo = partes["modelo"] or "Veículo"

            st.markdown(
                f"""
                <div class="vehicle-card">
                    <div class="vehicle-header">
                        <div>
                            <div class="vehicle-title">🚗 {veiculo_titulo}</div>
                            <div class="vehicle-sub">Motorista: {nome}</div>
                        </div>
                        {wa}
                    </div>
                    <div class="chips-inline-container">
                        {f'<span class="chip chip-muted">📍 {bairro}</span>' if bairro else ''}
                        {f'<span class="chip chip-blue">⭐ Líder: {lider}</span>' if lider else ''}
                        {f'<span class="chip chip-amber">🎨 {partes["cor"]}</span>' if partes["cor"] else ''}
                        {f'<span class="chip chip-muted">🔖 {partes["placa"]}</span>' if partes["placa"] else ''}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum apoiador com veículo registrado.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 4: PERFIL DEMOGRÁFICO
# ==========================================
if selected == "Perfil Demográfico":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">📊 Análise Demográfica</div>
            <div class="section-subtitle">Distribuição por faixa etária da base de eleitores</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if "Faixa_Etaria" in df.columns:
        df_faixa = df["Faixa_Etaria"].value_counts().reset_index()
        df_faixa.columns = ["Faixa Etária", "Quantidade"]
        fig_faixa = px.bar(df_faixa, x="Faixa Etária", y="Quantidade", text="Quantidade")
        fig_faixa.update_traces(marker_color=BLUE, textposition="outside")
        fig_faixa.update_layout(
            font_family=PLOTLY_FONT, font_color=TEXT,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=10), height=300,
        )
        st.plotly_chart(fig_faixa, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 5: DUPLICATAS (CPF / TÍTULO DE ELEITOR)
# ==========================================
if selected == "Duplicatas":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">⚠️ Cadastros Duplicados</div>
            <div class="section-subtitle">Pessoas cadastradas mais de uma vez com o mesmo CPF ou Título de Eleitor.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    tem_cpf = "CPF_PADRAO" in df.columns
    tem_titulo = "TITULO_PADRAO" in df.columns

    if not tem_cpf and not tem_titulo:
        st.info("Colunas de CPF e Título de Eleitor não encontradas na planilha.")
    else:
        df_dup = df.copy()
        df_dup["CPF_NUM"] = df_dup["CPF_PADRAO"].apply(lambda v: normalizar_documento(v, 11)) if tem_cpf else ""
        df_dup["TITULO_NUM"] = df_dup["TITULO_PADRAO"].apply(lambda v: normalizar_documento(v, 12)) if tem_titulo else ""

        def achar_duplicados(coluna_num: str) -> pd.DataFrame:
            validos = df_dup[df_dup[coluna_num] != ""]
            return validos[validos.duplicated(subset=coluna_num, keep=False)]

        dup_cpf = achar_duplicados("CPF_NUM") if tem_cpf else df_dup.iloc[0:0]
        dup_tit = achar_duplicados("TITULO_NUM") if tem_titulo else df_dup.iloc[0:0]

        grupos_cpf = dup_cpf["CPF_NUM"].nunique()
        grupos_tit = dup_tit["TITULO_NUM"].nunique()
        cadastros_envolvidos = len(set(dup_cpf.index) | set(dup_tit.index))

        alerta_cls = "kpi-alert" if (grupos_cpf + grupos_tit) > 0 else ""
        st.markdown(
            f"""
            <div class="kpi-grid">
                <div class="kpi-card {alerta_cls}"><div class="kpi-label">CPFs Duplicados</div><div class="kpi-value">{grupos_cpf}</div></div>
                <div class="kpi-card {alerta_cls}"><div class="kpi-label">Títulos Duplicados</div><div class="kpi-value">{grupos_tit}</div></div>
                <div class="kpi-card {alerta_cls}"><div class="kpi-label">Cadastros Envolvidos</div><div class="kpi-value">{cadastros_envolvidos}</div></div>
                <div class="kpi-card"><div class="kpi-label">Base Total</div><div class="kpi-value">{total_cadastros}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if grupos_cpf + grupos_tit == 0:
            st.success("✅ Nenhuma duplicidade de CPF ou Título de Eleitor encontrada na base.")
        else:
            c_d1, c_d2 = st.columns([1, 1])
            with c_d1:
                tipo_dup = st.selectbox("Tipo de duplicidade", ["Todos", "Somente CPF", "Somente Título"])
            with c_d2:
                busca_dup = st.text_input("Buscar por nome ou líder", placeholder="Digite para filtrar...", key="busca_dup")

            # Monta a lista de grupos: (tipo, documento_numérico, DataFrame do grupo)
            grupos = []
            if tipo_dup in ("Todos", "Somente CPF") and grupos_cpf > 0:
                for doc, sub in dup_cpf.groupby("CPF_NUM"):
                    grupos.append(("CPF", doc, sub))
            if tipo_dup in ("Todos", "Somente Título") and grupos_tit > 0:
                for doc, sub in dup_tit.groupby("TITULO_NUM"):
                    grupos.append(("Título", doc, sub))

            # Filtro de busca (nome ou líder) — mantém o grupo se qualquer membro bater
            if busca_dup:
                termo_dup = limpar_texto(busca_dup)
                grupos = [
                    g for g in grupos
                    if g[2]["NOME_PADRAO"].apply(limpar_texto).str.contains(termo_dup, na=False, regex=False).any()
                    or g[2]["LIDER_PADRAO"].str.contains(termo_dup, na=False, regex=False).any()
                ]

            # Ordena: grupos maiores primeiro
            grupos.sort(key=lambda g: (-len(g[2]), g[0], g[1]))

            st.markdown(
                f"<div style='color:{MUTED}; font-size:0.8rem; font-weight:600; margin-bottom:10px;'>{len(grupos)} grupo(s) de duplicidade encontrado(s)</div>",
                unsafe_allow_html=True,
            )

            # Tabela para exportação (construída junto com a exibição)
            linhas_export = []

            for tipo, doc, sub in grupos:
                if tipo == "CPF":
                    doc_txt = formatar_cpf(doc) if exibir_dados_sensiveis else mask_cpf(doc)
                else:
                    doc_txt = formatar_titulo(doc) if exibir_dados_sensiveis else mask_titulo(doc)

                qtd = len(sub)
                lideres_grupo = sorted({safe_title(x) for x in sub["LIDER_PADRAO"] if x})
                chip_lider = (
                    f'<span class="chip chip-amber">⭐ {len(lideres_grupo)} Líder(es)</span>'
                    if lideres_grupo else ""
                )

                st.markdown(
                    f"""
                    <div class="dup-card">
                        <div class="dup-title">{'🪪' if tipo == 'CPF' else '🗳️'} {tipo}: {doc_txt}</div>
                        <div class="chips-inline-container">
                            <span class="chip chip-red">⚠️ {qtd} cadastros</span>
                            {chip_lider}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"👥 Ver os {qtd} cadastros com este {tipo}"):
                    for _, r in sub.iterrows():
                        render_person_card(r, exibir_dados_sensiveis)

                for _, r in sub.iterrows():
                    linhas_export.append({
                        "Tipo de Duplicidade": tipo,
                        "Documento": doc_txt,
                        "Qtd. no Grupo": qtd,
                        "Nome": safe_title(r.get("NOME_PADRAO", "")),
                        "Liderança / Indicação": safe_title(r.get("LIDER_PADRAO", "")),
                        "Bairro": safe_title(r.get("BAIRRO_PADRAO", "")),
                        "Telefone / WhatsApp": r.get("CONTATO_PADRAO", ""),
                        "Data de Nascimento": r.get("NASCIMENTO_PADRAO", ""),
                        "Data do Cadastro": r.get("TIMESTAMP_PADRAO", ""),
                    })

            # Exportação das duplicatas
            if linhas_export:
                df_dup_export = pd.DataFrame(linhas_export)

                st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E6EBF2;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='font-size:0.95rem; font-weight:800; color:#071A2D;'>📥 Exportar duplicidades</h4>", unsafe_allow_html=True)

                buffer_dup = io.BytesIO()
                with pd.ExcelWriter(buffer_dup, engine="openpyxl") as writer:
                    df_dup_export.to_excel(writer, index=False, sheet_name="Duplicatas")

                col_x1, col_x2 = st.columns(2)
                with col_x1:
                    st.download_button(
                        label="📊 Baixar Duplicatas (.xlsx)",
                        data=buffer_dup.getvalue(),
                        file_name=f"Duplicatas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_dup_xlsx",
                    )
                with col_x2:
                    st.download_button(
                        label="📄 Baixar Duplicatas (.csv)",
                        data=df_dup_export.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"Duplicatas_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="dl_dup_csv",
                    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 6: RELATÓRIOS & EXPORTAÇÃO
# ==========================================
if selected == "Relatórios":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '''
        <div class="section-header-wrap">
            <div class="section-title">📥 Exportação de Relatórios e Dados</div>
            <div class="section-subtitle">Baixe a base de dados tratada para análises ou relatórios impressos.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    df_export = df.copy()

    # 1. Tratamento e Formatando Campos de Texto para visualização
    cols_para_formatar = {
        "NOME_PADRAO": "NOME_PADRAO",
        "LIDER_PADRAO": "LIDER_PADRAO",
        "BAIRRO_PADRAO": "BAIRRO_PADRAO",
        "MAE_PADRAO": "MAE_PADRAO",
        "LOCAL_VOTACAO_PADRAO": "LOCAL_VOTACAO_PADRAO"
    }
    for col_key in cols_para_formatar:
        if col_key in df_export.columns:
            df_export[col_key] = df_export[col_key].apply(safe_title)

    # 2. ORDENAÇÃO DECRESCENTE POR VOLUME DO LÍDER (Apoiadores do maior líder primeiro)
    if "LIDER_PADRAO" in df_export.columns:
        contagem_lideres = df_export["LIDER_PADRAO"].value_counts()
        df_export["TOTAL_LIDER"] = df_export["LIDER_PADRAO"].map(contagem_lideres).fillna(0)

        df_export = df_export.sort_values(
            by=["TOTAL_LIDER", "LIDER_PADRAO", "NOME_PADRAO"],
            ascending=[False, True, True]
        ).drop(columns=["TOTAL_LIDER"])

    # 3. Mascaramento opcional de dados sensíveis
    if not exibir_dados_sensiveis:
        if "CPF_PADRAO" in df_export.columns:
            df_export["CPF_PADRAO"] = df_export["CPF_PADRAO"].apply(mask_cpf)
        if "TITULO_PADRAO" in df_export.columns:
            df_export["TITULO_PADRAO"] = df_export["TITULO_PADRAO"].apply(mask_titulo)

    colunas_export = {
        "NOME_PADRAO": "Nome do Apoiador",
        "LIDER_PADRAO": "Liderança / Indicação",
        "BAIRRO_PADRAO": "Bairro",
        "CONTATO_PADRAO": "Telefone / WhatsApp",
        "NASCIMENTO_PADRAO": "Data de Nascimento",
        "MAE_PADRAO": "Nome da Mãe",
        "CPF_PADRAO": "CPF",
        "TITULO_PADRAO": "Título de Eleitor",
        "LOCAL_VOTACAO_PADRAO": "Local de Votação",
        "VEICULO_INFO_PADRAO": "Veículo",
    }
    cols_existentes = [c for c in colunas_export.keys() if c in df_export.columns]
    df_export_final = df_export[cols_existentes].rename(columns=colunas_export)

    col_e1, col_e2 = st.columns(2)

    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        df_export_final.to_excel(writer, index=False, sheet_name="Apoiadores Por Lideranca")
    excel_data = buffer_excel.getvalue()

    with col_e1:
        st.download_button(
            label="📊 Baixar Relatório em Excel (.xlsx)",
            data=excel_data,
            file_name=f"Relatorio_Apoiadores_Por_Lider_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    csv_data = df_export_final.to_csv(index=False).encode("utf-8-sig")
    with col_e2:
        st.download_button(
            label="📄 Baixar Relatório em CSV",
            data=csv_data,
            file_name=f"Relatorio_Apoiadores_Por_Lider_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size:0.95rem; font-weight:800; color:#071A2D;'>Pré-visualização da Tabela de Exportação (Ordenada por Liderança):</h4>", unsafe_allow_html=True)
    st.dataframe(df_export_final, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
