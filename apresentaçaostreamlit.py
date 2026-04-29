import streamlit as st
from datetime import datetime
import json
import os
import requests
import shutil
from pathlib import Path

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
    .backup-info {
        background: #1e3a2e;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Constantes ──────────────────────────────────────────────────────────────
ARQUIVO = "anotacoes.json"
ARQUIVO_BACKUP = "anotacoes_backup.json"
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

# ── Funções de backup e recuperação ─────────────────────────────────────────
def criar_backup():
    """Cria um backup do arquivo de anotações"""
    if os.path.exists(ARQUIVO):
        try:
            shutil.copy2(ARQUIVO, ARQUIVO_BACKUP)
            return True
        except Exception as e:
            print(f"Erro no backup: {e}")
            return False
    return False

def restaurar_backup():
    """Restaura anotações do backup"""
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            shutil.copy2(ARQUIVO_BACKUP, ARQUIVO)
            return True
        except Exception as e:
            print(f"Erro na restauração: {e}")
            return False
    return False

def carregar():
    """Carrega anotações com verificação de integridade"""
    # Tenta carregar do arquivo principal
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list) and len(dados) > 0:
                    return dados
                else:
                    # Arquivo vazio ou corrompido, tenta backup
                    if restaurar_backup():
                        with open(ARQUIVO, "r", encoding="utf-8") as f:
                            return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
            # Tenta restaurar do backup
            if restaurar_backup():
                try:
                    with open(ARQUIVO, "r", encoding="utf-8") as f:
                        return json.load(f)
                except:
                    pass
    
    # Se não existe ou falhou, cria anotações iniciais
    anotacoes_iniciais = [
        {"id": 1, "titulo": "E = mc²", "categoria": "Fisica", "texto": "Energia equivale a massa vezes a velocidade da luz ao quadrado.", "data": datetime.now().strftime("%d/%m/%Y %H:%M")},
        {"id": 2, "titulo": "Redes Neurais", "categoria": "IA", "texto": "Redes neurais artificiais são inspiradas no cérebro humano.", "data": datetime.now().strftime("%d/%m/%Y %H:%M")},
    ]
    salvar(anotacoes_iniciais)
    criar_backup()
    return anotacoes_iniciais

def salvar(notas):
    """Salva anotações com verificação e backup automático"""
    try:
        # Salva arquivo principal
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(notas, f, ensure_ascii=False, indent=2)
        
        # Cria backup automaticamente
        criar_backup()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def exportar_anotacoes():
    """Exporta anotações para JSON"""
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return f.read()
    return "[]"

def importar_anotacoes(conteudo):
    """Importa anotações de um JSON"""
    try:
        dados = json.loads(conteudo)
        if isinstance(dados, list):
            salvar(dados)
            return True
    except:
        return False
    return False

def perguntar_claude(api_key: str, historico: list, pergunta: str) -> str:
    headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
    mensagens = [{"role": msg["role"], "content": msg["content"]} for msg in historico]
    mensagens.append({"role": "user", "content": pergunta})
    payload = {"model": CLAUDE_MODEL, "max_tokens": 1000, "system": "Você é um assistente de estudos inteligente. Responda sempre em português brasileiro de forma clara e didática.", "messages": mensagens}
    try:
        resp = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401: return "❌ API Key inválida."
        elif resp.status_code == 429: return "⚠️ Limite de requisições atingido."
        return f"❌ Erro: {str(e)}"
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# ── Estado da sessão ─────────────────────────────────────────────────────────
if "notas" not in st.session_state:
    st.session_state.notas = carregar()
if "prox_id" not in st.session_state:
    ids = [n["id"] for n in st.session_state.notas]
    st.session_state.prox_id = max(ids) + 1 if ids else 1
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📝 Minhas Anotações + IA</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Organize seus estudos, converse com Claude e acompanhe seu progresso</div>', unsafe_allow_html=True)

# ── Informação de backup ─────────────────────────────────────────────────────
col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
with col_info1:
    if os.path.exists(ARQUIVO):
        mod_time = datetime.fromtimestamp(os.path.getmtime(ARQUIVO)).strftime("%d/%m/%Y %H:%M:%S")
        st.caption(f"💾 Último salvamento: {mod_time}")
with col_info2:
    if st.button("📦 Criar Backup Agora", use_container_width=True):
        if criar_backup():
            st.success("Backup criado!")
            st.rerun()
with col_info3:
    if st.button("🔄 Restaurar Backup", use_container_width=True):
        if restaurar_backup():
            st.session_state.notas = carregar()
            st.success("Backup restaurado!")
            st.rerun()
        else:
            st.error("Nenhum backup encontrado!")

# ── Estatísticas ─────────────────────────────────────────────────────────────
notas = st.session_state.notas
total = len(notas)
hoje = datetime.now().strftime("%d/%m/%Y")
qtd_hoje = sum(1 for n in notas if n["data"].startswith(hoje))
cats_usadas = len({n["categoria"] for n in notas})
palavras = sum(len(n["texto"].split()) for n in notas)

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in [(c1, total, "Total"), (c2, qtd_hoje, "Hoje"), (c3, cats_usadas, "Categorias"), (c4, palavras, "Palavras")]:
    col.markdown(f'<div class="stat-box"><div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Key Claude")
    api_key = st.text_input("Cole sua API Key aqui", type="password", placeholder="sk-ant-...", help="Obtenha em console.anthropic.com")
    if api_key: 
        st.success("✅ API Key configurada!")
    else: 
        st.warning("⚠️ Configure sua API Key para usar o Chat IA")
    st.markdown("---")
    
    st.markdown("### ➕ Nova Anotação")
    titulo = st.text_input("Título", placeholder="Ex: Equação de Schrödinger")
    categoria = st.selectbox("Categoria", CATEGORIAS)
    texto = st.text_area("Conteúdo", placeholder="Escreva sua anotação aqui...", height=150)
    col_s, col_l = st.columns(2)
    salvar_btn = col_s.button("💾 Salvar", use_container_width=True)
    limpar_btn = col_l.button("🗑️ Limpar", use_container_width=True)
    
    if salvar_btn and titulo and texto:
        nova = {
            "id": st.session_state.prox_id, 
            "titulo": titulo, 
            "categoria": categoria, 
            "texto": texto, 
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.session_state.notas.insert(0, nova)
        st.session_state.prox_id += 1
        if salvar(st.session_state.notas):
            st.success("Anotação salva!")
            st.rerun()
        else:
            st.error("Erro ao salvar!")
    elif salvar_btn: 
        st.warning("Preencha título e conteúdo.")
    
    st.markdown("---")
    st.markdown("### 🔍 Filtros")
    busca = st.text_input("Buscar", placeholder="Digite para buscar...")
    filtro = st.selectbox("Categoria", ["Todas"] + CATEGORIAS)
    ordem = st.radio("Ordenar por", ["Mais recentes", "Mais antigas"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 💾 Exportar/Importar")
    
    # Botão exportar
    export_data = exportar_anotacoes()
    st.download_button(
        label="📥 Exportar Anotações (JSON)",
        data=export_data,
        file_name=f"anotacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    # Upload para importar
    uploaded_file = st.file_uploader("📤 Importar Anotações", type=["json"], key="import_uploader")
    if uploaded_file is not None:
        conteudo = uploaded_file.read().decode("utf-8")
        if importar_anotacoes(conteudo):
            st.session_state.notas = carregar()
            st.success("Anotações importadas com sucesso!")
            st.rerun()
        else:
            st.error("Arquivo inválido!")

# ── Abas principais ──────────────────────────────────────────────────────────
aba1, aba2, aba3 = st.tabs(["📝 Anotações", "🤖 Chat com Claude IA", "📚 Documentação"])

# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — ANOTAÇÕES
# ════════════════════════════════════════════════════════════════════════════
with aba1:
    filtradas = [
        n for n in st.session_state.notas 
        if (filtro == "Todas" or n["categoria"] == filtro) 
        and (not busca or busca.lower() in n["titulo"].lower() or busca.lower() in n["texto"].lower())
    ]
    if ordem == "Mais antigas": 
        filtradas = list(reversed(filtradas))
    
    if not filtradas: 
        st.info("Nenhuma anotação encontrada.")
    else:
        for nota in filtradas:
            badge_cls = CORES_BADGE.get(nota["categoria"], "badge-Outros")
            st.markdown(
                f'<div class="note-card">'
                f'<span class="badge {badge_cls}">{nota["categoria"]}</span>'
                f'<div class="note-title">{nota["titulo"]}</div>'
                f'<div class="note-text">{nota["texto"]}</div>'
                f'<small style="color:#45475a">{nota["data"]}</small>'
                f'</div>', 
                unsafe_allow_html=True
            )
            col1, col2, col3 = st.columns([1, 1, 1])
            
            if col1.button("🤖 IA", key=f"ia_{nota['id']}"):
                if not api_key: 
                    st.warning("Configure sua API Key na sidebar!")
                else:
                    with st.spinner("Claude pensando..."):
                        prompt = f"Resuma esta anotação e crie 3 questões:\n**{nota['titulo']}**\n{nota['texto']}"
                        resposta = perguntar_claude(api_key, [], prompt)
                        st.session_state.historico_chat.append({"role": "user", "content": prompt})
                        st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
                    st.success("Resposta enviada para o Chat IA!")
                    st.rerun()
            
            if col2.button("💡 Explicar", key=f"exp_{nota['id']}"):
                if not api_key: 
                    st.warning("Configure sua API Key na sidebar!")
                else:
                    with st.spinner("Claude pensando..."):
                        prompt = f"Explique de forma simples:\n**{nota['titulo']}**\n{nota['texto']}"
                        resposta = perguntar_claude(api_key, [], prompt)
                        st.session_state.historico_chat.append({"role": "user", "content": prompt})
                        st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
                    st.success("Resposta enviada para o Chat IA!")
                    st.rerun()
            
            if col3.button("🗑️ Apagar", key=f"del_{nota['id']}"):
                st.session_state.notas = [n for n in st.session_state.notas if n["id"] != nota["id"]]
                if salvar(st.session_state.notas):
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
        col_s1, col_s2, col_s3 = st.columns(3)
        if col_s1.button("📚 Resumir anotações"):
            todas = "\n".join([f"- {n['titulo']}: {n['texto'][:80]}..." for n in st.session_state.notas[:5]])
            prompt = f"Faça um resumo geral:\n{todas}"
            with st.spinner("Claude pensando..."): 
                resposta = perguntar_claude(api_key, st.session_state.historico_chat, prompt)
            st.session_state.historico_chat.append({"role": "user", "content": prompt})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()
        
        if col_s2.button("🎯 Criar quiz"):
            todas = "\n".join([f"- {n['titulo']}: {n['texto'][:80]}..." for n in st.session_state.notas[:5]])
            prompt = f"Crie um quiz com 5 questões:\n{todas}"
            with st.spinner("Claude pensando..."): 
                resposta = perguntar_claude(api_key, st.session_state.historico_chat, prompt)
            st.session_state.historico_chat.append({"role": "user", "content": prompt})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()
        
        if col_s3.button("🗑️ Limpar chat"):
            st.session_state.historico_chat = []
            st.rerun()
        
        st.markdown("---")
        
        if not st.session_state.historico_chat: 
            st.info("Nenhuma conversa ainda. Faça uma pergunta abaixo!")
        else:
            for msg in st.session_state.historico_chat:
                if msg["role"] == "user": 
                    st.markdown(f'<div class="chat-label">Você</div><div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else: 
                    st.markdown(f'<div class="chat-label">🤖 Claude</div><div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.form("chat_form", clear_on_submit=True):
            pergunta = st.text_input("Sua pergunta", placeholder="Ex: Explique a equação de Schrödinger, crie questões sobre funções...")
            enviar = st.form_submit_button("Enviar ↗", use_container_width=True)
        
        if enviar and pergunta:
            with st.spinner("Claude pensando..."): 
                resposta = perguntar_claude(api_key, st.session_state.historico_chat, pergunta)
            st.session_state.historico_chat.append({"role": "user", "content": pergunta})
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta})
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# ABA 3 — DOCUMENTAÇÃO (resumida para não repetir)
# ════════════════════════════════════════════════════════════════════════════
with aba3:
    st.markdown("## 📚 Documentação do Sistema")
    st.markdown("---")
    
    st.markdown("### 💾 Sistema de Persistência de Dados")
    st.markdown("""
    **Como os dados são salvos:**
    
    - ✅ **Arquivo JSON local:** Todas as anotações são salvas no arquivo `anotacoes.json`
    - ✅ **Backup automático:** A cada salvamento, uma cópia é criada em `anotacoes_backup.json`
    - ✅ **Recuperação automática:** Se o arquivo principal corromper, o sistema restaura do backup
    - ✅ **Exportar/Importar:** Você pode baixar suas anotações e restaurar em outro computador
    
    **Por que as anotações não somem mais:**
    
    Antes, as anotações ficavam apenas na memória (Session State). Quando o Streamlit reiniciava, os dados eram perdidos.
    
    Agora, a cada alteração (salvar, editar, apagar), o sistema **salva imediatamente no arquivo JSON**, garantindo que os dados persistam mesmo após reboot.
    """)
    
    st.info("💡 **Dica:** Use os botões 'Criar Backup Agora' e 'Restaurar Backup' para maior segurança!")
    
    st.markdown("---")
    
    st.markdown("### 🚀 Recursos de Segurança Adicionados")
    st.markdown("""
    - 🔄 **Backup automático** a cada salvamento
    - 📥 **Exportação** completa dos dados
    - 📤 **Importação** de backups anteriores
    - 🛡️ **Verificação de integridade** dos arquivos
    - ⏰ **Timestamp do último salvamento**
    """)

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#45475a'>📝 App de Anotações + Claude IA — Dados salvos localmente em JSON | Versão 3.0 (Com persistência)</small>", 
    unsafe_allow_html=True
)