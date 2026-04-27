import streamlit as st
from datetime import datetime
import json
import os
import requests

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Minhas Anotações",
    page_icon="📝",
    layout="wide"
)

# ── Estilos CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .note-card {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .note-title {
        font-size: 16px;
        font-weight: 600;
        color: #cdd6f4;
        margin-bottom: 8px;
    }
    .note-text {
        font-size: 14px;
        color: #a6adc8;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .badge-Fisica       { background:#1e3a5f; color:#89b4fa; }
    .badge-IA           { background:#1e3a2e; color:#a6e3a1; }
    .badge-Mecatronica  { background:#3a2e1e; color:#fab387; }
    .badge-Doutorado    { background:#2e1e3a; color:#cba6f7; }
    .badge-Matematica   { background:#3a1e1e; color:#f38ba8; }
    .badge-Outros       { background:#2a2a2a; color:#a6adc8; }
    .stat-box {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .stat-val { font-size: 24px; font-weight: 700; color: #cdd6f4; }
    .stat-lbl { font-size: 12px; color: #6c7086; margin-top: 2px; }
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #cdd6f4;
        margin-bottom: 4px;
    }
    .main-sub {
        font-size: 14px;
        color: #6c7086;
        margin-bottom: 20px;
    }
    .chat-msg-user {
        background: #2a2a3e;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
        color: #cdd6f4;
        font-size: 14px;
        text-align: right;
    }
    .chat-msg-ai {
        background: #1e3a2e;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
        color: #a6e3a1;
        font-size: 14px;
    }
    .chat-label {
        font-size: 11px;
        color: #6c7086;
        margin-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Constantes ──────────────────────────────────────────────────────────────
ARQUIVO = "anotacoes.json"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-sonnet-20240229"

CORES_BADGE = {
    "Fisica":      "badge-Fisica",
    "IA":          "badge-IA",
    "Mecatronica": "badge-Mecatronica",
    "Doutorado":   "badge-Doutorado",
    "Matematica":  "badge-Matematica",
    "Outros":      "badge-Outros",
}
CATEGORIAS = list(CORES_BADGE.keys())


# ── Funções de dados ────────────────────────────────────────────────────────
def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {
            "id": 1,
            "titulo": "E = mc²",
            "categoria": "Fisica",
            "texto": "Energia equivale a massa vezes a velocidade da luz ao quadrado. "
                     "Com m=0,0004 kg e c=3×10⁸ m/s → E = 3,6 × 10¹³ Joules.",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        },
        {
            "id": 2,
            "titulo": "Redes Neurais",
            "categoria": "IA",
            "texto": "Redes neurais artificiais são inspiradas no cérebro humano. "
                     "Camadas de neurônios artificiais processam informação em paralelo.",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        },
        {
            "id": 3,
            "titulo": "Plano Acadêmico",
            "categoria": "Doutorado",
            "texto": "Objetivo: Passar no vestibular da UNICAMP 2026 → Bacharelado → Mestrado → Doutorado.",
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        },
    ]


def salvar(notas):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=2)


# ── Função Claude API ────────────────────────────────────────────────────────
def perguntar_claude(api_key: str, historico: list, pergunta: str) -> str:
    """Envia mensagem para a API do Claude e retorna a resposta."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    # Monta histórico de mensagens
    mensagens = []
    for msg in historico:
        mensagens.append({"role": msg["role"], "content": msg["content"]})
    mensagens.append({"role": "user", "content": pergunta})

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1000,
        "system": (
            "Você é um assistente de estudos inteligente integrado a um app de anotações. "
            "Ajude o usuário a entender melhor seus estudos, resumir conteúdos, criar questões "
            "de revisão e explicar conceitos de forma clara e didática. "
            "Responda sempre em português brasileiro."
        ),
        "messages": mensagens,
    }

    try:
        resp = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return "❌ API Key inválida. Verifique sua chave na sidebar."
        elif resp.status_code == 429:
            return "⚠️ Limite de requisições atingido. Aguarde um momento."
        else:
            return f"❌ Erro na API: {str(e)}"
    except Exception as e:
        return f"❌ Erro ao conectar com Claude: {str(e)}"


# ── Estado da sessão ─────────────────────────────────────────────────────────
if "notas" not in st.session_state:
    st.session_state.notas = carregar()

if "prox_id" not in st.session_state:
    ids = [n["id"] for n in st.session_state.notas]
    st.session_state.prox_id = max(ids) + 1 if ids else 1

if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

if "aba" not in st.session_state:
    st.session_state.aba = "anotacoes"


# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📝 Minhas Anotações + IA</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Organize seus estudos e converse com o Claude</div>', unsafe_allow_html=True)

# ── Estatísticas ─────────────────────────────────────────────────────────────
notas = st.session_state.notas
total       = len(notas)
hoje        = datetime.now().strftime("%d/%m/%Y")
qtd_hoje    = sum(1 for n in notas if n["data"].startswith(hoje))
cats_usadas = len({n["categoria"] for n in notas})
palavras    = sum(len(n["texto"].split()) for n in notas)

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in [
    (c1, total,      "Total"),
    (c2, qtd_hoje,   "Hoje"),
    (c3, cats_usadas,"Categorias"),
    (c4, palavras,   "Palavras"),
]:
    col.markdown(
        f'<div class="stat-box"><div class="stat-val">{val}</div>'
        f'<div class="stat-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # API Key
    st.markdown("### 🔑 API Key Claude")
    api_key = st.text_input(
        "Cole sua API Key aqui",
        type="password",
        placeholder="sk-ant-...",
        help="Obtenha em console.anthropic.com"
    )
    if api_key:
        st.success("✅ API Key configurada!")
    else:
        st.warning("⚠️ Configure sua API Key para usar o Chat IA")

    st.markdown("---")

    # Nova anotação
    st.markdown("### ➕ Nova Anotação")
    titulo    = st.text_input("Título", placeholder="Ex: Equação de Schrödinger")
    categoria = st.selectbox("Categoria", CATEGORIAS)
    texto     = st.text_area("Conteúdo", placeholder="Escreva sua anotação aqui...", height=150)

    col_s, col_l = st.columns(2)
    salvar_btn = col_s.button("💾 Salvar", use_container_width=True)
    limpar_btn = col_l.button("🗑️ Limpar", use_container_width=True)

    if salvar_btn:
        if titulo and texto:
            nova = {
                "id":        st.session_state.prox_id,
                "titulo":    titulo,
                "categoria": categoria,
                "texto":     texto,
                "data":      datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            st.session_state.notas.insert(0, nova)
            st.session_state.prox_id += 1
            salvar(st.session_state.notas)
            st.success("Anotação salva!")
            st.rerun()
        else:
            st.warning("Preencha título e conteúdo.")

    st.markdown("---")

    # Filtros
    st.markdown("### 🔍 Filtros")
    busca  = st.text_input("Buscar", placeholder="Digite para buscar...")
    filtro = st.selectbox("Categoria", ["Todas"] + CATEGORIAS)
    ordem  = st.radio("Ordenar por", ["Mais recentes", "Mais antigas"], horizontal=True)

# ── Abas principais ──────────────────────────────────────────────────────────
aba1, aba2 = st.tabs(["📝 Anotações", "🤖 Chat com Claude IA"])

# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — ANOTAÇÕES
# ════════════════════════════════════════════════════════════════════════════
with aba1:
    filtradas = [
        n for n in st.session_state.notas
        if (filtro == "Todas" or n["categoria"] == filtro)
        and (not busca or busca.lower() in n["titulo"].lower()
             or busca.lower() in n["texto"].lower())
    ]

    if ordem == "Mais antigas":
        filtradas = list(reversed(filtradas))

    if not filtradas:
        st.info("Nenhuma anotação encontrada.")
    else:
        for nota in filtradas:
            badge_cls = CORES_BADGE.get(nota["categoria"], "badge-Outros")
            st.markdown(f"""
            <div class="note-card">
                <span class="badge {badge_cls}">{nota['categoria']}</span>
                <div class="note-title">{nota['titulo']}</div>
                <div class="note-text">{nota['texto']}</div>
                <small style="color:#45475a">{nota['data']}</small>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 4])

            # Botão resumir com IA
            if col1.button("🤖 IA", key=f"ia_{nota['id']}"):
                if not api_key:
                    st.warning("Configure sua API Key na sidebar!")
                else:
                    with st.spinner("Claude pensando..."):
                        prompt = (
                            f"Resuma esta anotação de forma clara e crie 3 questões "
                            f"de revisão sobre o tema:\n\n"
                            f"**{nota['titulo']}**\n{nota['texto']}"
                        )
                        resposta = perguntar_claude(api_key, [], prompt)
                        st.session_state.historico_chat.append(
                            {"role": "user", "content": prompt}
                        )
                        st.session_state.historico_chat.append(
                            {"role": "assistant", "content": resposta}
                        )
                    st.success("Resposta enviada para o Chat IA! Clique na aba 🤖")

            # Botão explicar
            if col2.button("💡 Explicar", key=f"exp_{nota['id']}"):
                if not api_key:
                    st.warning("Configure sua API Key na sidebar!")
                else:
                    with st.spinner("Claude pensando..."):
                        prompt = (
                            f"Explique de forma simples e didática o seguinte conceito "
                            f"para um estudante de 18 anos:\n\n"
                            f"**{nota['titulo']}**\n{nota['texto']}"
                        )
                        resposta = perguntar_claude(api_key, [], prompt)
                        st.session_state.historico_chat.append(
                            {"role": "user", "content": prompt}
                        )
                        st.session_state.historico_chat.append(
                            {"role": "assistant", "content": resposta}
                        )
                    st.success("Resposta enviada para o Chat IA! Clique na aba 🤖")

            # Botão apagar
            if col3.button("🗑️ Apagar", key=f"del_{nota['id']}"):
                st.session_state.notas = [
                    n for n in st.session_state.notas if n["id"] != nota["id"]
                ]
                salvar(st.session_state.notas)
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — CHAT COM CLAUDE
# ════════════════════════════════════════════════════════════════════════════
with aba2:
    st.markdown("### 🤖 Converse com o Claude")

    if not api_key:
        st.warning("⚠️ Configure sua API Key do Claude na sidebar para usar o chat!")
        st.markdown("**Como obter sua API Key:**")
        st.markdown("1. Acesse **console.anthropic.com**")
        st.markdown("2. Crie uma conta gratuita")
        st.markdown("3. Vá em **API Keys** e crie uma chave")
        st.markdown("4. Cole na sidebar à esquerda")
    else:
        # Sugestões rápidas
        st.markdown("**💡 Sugestões rápidas:**")
        col_s1, col_s2, col_s3 = st.columns(3)

        if col_s1.button("📚 Resumir anotações"):
            todas = "\n".join(
                [f"- {n['titulo']}: {n['texto'][:80]}..." for n in st.session_state.notas[:5]]
            )
            prompt = f"Faça um resumo geral das minhas anotações:\n{todas}"
            with st.spinner("Claude pensando..."):
                resposta = perguntar_claude(api_key, st.session_state.historico_chat, prompt)
            st.session_state.historico_chat.append({"role": "user", "content": prompt})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()

        if col_s2.button("🎯 Criar quiz"):
            todas = "\n".join(
                [f"- {n['titulo']}: {n['texto'][:80]}..." for n in st.session_state.notas[:5]]
            )
            prompt = f"Crie um quiz com 5 questões baseado nas minhas anotações:\n{todas}"
            with st.spinner("Claude pensando..."):
                resposta = perguntar_claude(api_key, st.session_state.historico_chat, prompt)
            st.session_state.historico_chat.append({"role": "user", "content": prompt})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()

        if col_s3.button("🗑️ Limpar chat"):
            st.session_state.historico_chat = []
            st.rerun()

        st.markdown("---")

        # Histórico do chat
        if not st.session_state.historico_chat:
            st.info("Nenhuma conversa ainda. Faça uma pergunta abaixo!")
        else:
            for msg in st.session_state.historico_chat:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-label">Você</div>'
                        f'<div class="chat-msg-user">{msg["content"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-label">🤖 Claude</div>'
                        f'<div class="chat-msg-ai">{msg["content"]}</div>',
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # Input do chat
        with st.form("chat_form", clear_on_submit=True):
            pergunta = st.text_input(
                "Sua pergunta",
                placeholder="Ex: Explique a equação de Schrödinger, crie questões sobre funções...",
            )
            enviar = st.form_submit_button("Enviar ↗", use_container_width=True)

        if enviar and pergunta:
            with st.spinner("Claude pensando..."):
                resposta = perguntar_claude(
                    api_key, st.session_state.historico_chat, pergunta
                )
            st.session_state.historico_chat.append({"role": "user",      "content": pergunta})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#45475a'>📝 App de Anotações + Claude IA — desenvolvido com Python + Streamlit</small>",
    unsafe_allow_html=True,
)


