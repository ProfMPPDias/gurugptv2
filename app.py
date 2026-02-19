"""
GuruGPT — Streamlit AI Chatbot with Ollama
Anonymous multi-session chatbot with PDF analysis and conversation history.
"""

import uuid
import time
import streamlit as st
import fitz  # PyMuPDF

# ─────────────────────────────────────────────────
# Page config — MUST be first Streamlit call
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="GuruGPT",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────
# Custom CSS — premium dark theme + resizable sidebar
# ─────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@700;800;900&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary: #0d0d14;
    --bg-secondary: #13131f;
    --bg-card: #1a1a2e;
    --bg-sidebar: #0f0f1a;
    --accent: #7c3aed;
    --accent-glow: #9d5ffc;
    --accent-light: #c4b5fd;
    --text-primary: #f0eeff;
    --text-secondary: #a89fd0;
    --border: #2a2a45;
    --user-bubble: #2d1b69;
    --assistant-bubble: #141424;
    --danger: #ef4444;
    --success: #10b981;
    --font-main: 'Inter', sans-serif;
    --font-brand: 'Outfit', sans-serif;
}

/* ── Global reset ── */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: var(--font-main);
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* ── Streamlit main app bg ── */
.stApp {
    background: linear-gradient(135deg, #0d0d14 0%, #12101e 50%, #0a0a15 100%);
    min-height: 100vh;
}

/* ── Sidebar — always visible, never collapsible ── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
    resize: horizontal;
    overflow: auto;
    min-width: 220px !important;
    max-width: 500px;
    transform: none !important;
    translate: none !important;
    margin-left: 0 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

/* Target the inner section Streamlit animates to slide the sidebar out */
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div {
    transform: none !important;
    translate: none !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.75rem;
}

/* ── Main content area ── */
[data-testid="stMain"] .block-container {
    padding-top: 1.5rem;
    max-width: 860px;
    margin: 0 auto;
}

/* ── GuruGPT Logo ── */
.gurugpt-logo {
    text-align: center;
    padding: 1.2rem 0 0.6rem;
    user-select: none;
}

.gurugpt-logo .icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    border-radius: 20px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    box-shadow: 0 0 32px rgba(124, 58, 237, 0.55), 0 0 8px rgba(124, 58, 237, 0.3);
    margin: 0 auto 12px;
    font-size: 2.2rem;
    animation: logoPulse 3s ease-in-out infinite;
}

@keyframes logoPulse {
    0%, 100% { box-shadow: 0 0 28px rgba(124,58,237,.5), 0 0 6px rgba(124,58,237,.3); }
    50%       { box-shadow: 0 0 48px rgba(124,58,237,.7), 0 0 16px rgba(124,58,237,.5); }
}

.gurugpt-logo h1 {
    font-family: var(--font-brand);
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #c4b5fd 0%, #7c3aed 50%, #4f46e5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
    line-height: 1;
}

.gurugpt-logo p {
    color: var(--text-secondary);
    font-size: 0.87rem;
    font-weight: 400;
    margin-top: 6px;
    letter-spacing: 0.4px;
}

/* ── Divider ── */
.g-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 0.8rem 0 1.2rem;
}

/* ── Sidebar title ── */
.sidebar-title {
    font-family: var(--font-brand);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin: 0.4rem 0 0.8rem 0.2rem;
}

/* ── Conversation item ── */
.conv-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0.55rem 0.7rem;
    border-radius: 10px;
    cursor: pointer;
    margin-bottom: 4px;
    transition: background 0.15s ease;
    background: transparent;
    border: 1px solid transparent;
}

.conv-item:hover {
    background: rgba(124,58,237,0.12);
    border-color: rgba(124,58,237,0.25);
}

.conv-item.active {
    background: rgba(124,58,237,0.2);
    border-color: rgba(124,58,237,0.45);
}

.conv-title {
    flex: 1;
    font-size: 0.84rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 160px;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    margin-bottom: 0.2rem;
}

[data-testid="stChatMessage"][data-testid*="user"] .stChatMessageContent {
    background: var(--user-bubble) !important;
    border-radius: 18px 18px 4px 18px !important;
    border: 1px solid rgba(124,58,237,0.3);
}

[data-testid="stChatMessage"][data-testid*="assistant"] .stChatMessageContent {
    background: var(--assistant-bubble) !important;
    border-radius: 18px 18px 18px 4px !important;
    border: 1px solid var(--border);
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stSelectbox > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.25) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card);
    border: 1.5px dashed var(--border);
    border-radius: 12px;
    padding: 0.8rem;
    transition: border-color 0.2s;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent);
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.08);
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2), 0 0 20px rgba(124,58,237,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: var(--font-main);
    transition: all 0.2s ease;
    box-shadow: 0 2px 12px rgba(124,58,237,0.3);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,58,237,0.45);
}

.stButton > button:active {
    transform: translateY(0);
}

/* ── Danger/delete button ── */
.delete-btn > button {
    background: transparent !important;
    color: var(--danger) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    box-shadow: none !important;
    padding: 0.2rem 0.6rem !important;
    font-size: 0.75rem !important;
    border-radius: 8px !important;
}

.delete-btn > button:hover {
    background: rgba(239,68,68,0.15) !important;
    border-color: var(--danger) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── PDF badge ── */
.pdf-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.78rem;
    color: var(--accent-light);
    margin-bottom: 0.6rem;
}

/* ── Status bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: blink 2s ease-in-out infinite;
}

.status-dot.offline {
    background: var(--danger);
    box-shadow: 0 0 6px var(--danger);
    animation: none;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Wrappers for model selector row ── */
.model-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.9rem 1.1rem 0.7rem;
    margin-bottom: 1.1rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a45; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Error / warning alerts ── */
.stAlert {
    border-radius: 10px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── Hide Streamlit default header / footer ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ── Sidebar new chat button full width ── */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    margin-bottom: 0.5rem;
}

/* ── Hide sidebar collapse & expand buttons (sidebar is always visible) ── */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* ── Footer ── */
.gurugpt-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    padding: 0.55rem 1rem;
    font-size: 0.75rem;
    color: #6b6a8a;
    background: rgba(13,13,20,0.92);
    backdrop-filter: blur(8px);
    border-top: 1px solid #1e1e32;
    z-index: 1000;
    letter-spacing: 0.3px;
    font-family: var(--font-main);
}
.gurugpt-footer span {
    color: #ef4444;
}
/* Push chat content above footer */
[data-testid="stMain"] .block-container {
    padding-bottom: 3rem !important;
}
</style>
"""

# ── Floating sidebar-reopen button injected directly to document.body ──
# This runs independently of Streamlit's component tree so it can never
# be hidden when the sidebar collapses.
SIDEBAR_TOGGLE_JS = """
<script>
(function () {
    const BTN_ID = 'gurugpt-sidebar-open-btn';

    /* ── Build the button once ── */
    function buildBtn() {
        const existing = document.getElementById(BTN_ID);
        if (existing) return existing;

        const btn = document.createElement('button');
        btn.id = BTN_ID;
        btn.title = 'Abrir painel lateral';
        btn.textContent = '☰';
        Object.assign(btn.style, {
            position:     'fixed',
            top:          '50vh',
            left:         '0',
            transform:    'translateY(-50%)',
            zIndex:       '2147483647',
            background:   'linear-gradient(180deg,#7c3aed 0%,#4f46e5 100%)',
            color:        'white',
            border:       'none',
            borderRadius: '0 14px 14px 0',
            width:        '40px',
            height:       '56px',
            fontSize:     '1.2rem',
            cursor:       'pointer',
            display:      'none',
            alignItems:   'center',
            justifyContent: 'center',
            boxShadow:    '4px 0 24px rgba(124,58,237,0.75)',
            transition:   'width .2s, box-shadow .2s',
            fontFamily:   'sans-serif',
            lineHeight:   '1',
        });

        btn.addEventListener('mouseenter', () => {
            btn.style.width = '50px';
            btn.style.boxShadow = '6px 0 32px rgba(124,58,237,0.95)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.width = '40px';
            btn.style.boxShadow = '4px 0 24px rgba(124,58,237,0.75)';
        });
        btn.addEventListener('click', openSidebar);

        document.body.appendChild(btn);
        return btn;
    }

    /* ── Click the hidden Streamlit arrow to expand the sidebar ── */
    function openSidebar() {
        // Streamlit places the expand arrow in [data-testid="collapsedControl"]
        const arrow = document.querySelector('[data-testid="collapsedControl"] button')
                   || document.querySelector('[data-testid="collapsedControl"]');
        if (arrow) { arrow.click(); return; }

        // Fallback: look for any sidebar toggle button
        const toggle = document.querySelector('[data-testid="stSidebarCollapseButton"] button')
                    || document.querySelector('button[kind="header"]');
        if (toggle) toggle.click();
    }

    /* ── Detect whether the sidebar is currently collapsed ── */
    function isSidebarVisible() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return false;
        const w = sidebar.getBoundingClientRect().width;
        return w > 60;   // anything below 60 px is considered collapsed
    }

    /* ── Update button display ── */
    function sync() {
        const btn = buildBtn();
        btn.style.display = isSidebarVisible() ? 'none' : 'flex';
    }

    /* ── Pulse glow (CSS keyframes won't work inline, use JS animation) ── */
    function startPulse(btn) {
        let t = 0;
        setInterval(() => {
            t += 0.05;
            const glow = 0.55 + 0.3 * Math.sin(t);
            btn.style.boxShadow = `4px 0 ${Math.round(20 + 16 * Math.sin(t))}px rgba(124,58,237,${glow.toFixed(2)})`;
        }, 50);
    }

    /* ── Boot: wait until body exists then initialise ── */
    function boot() {
        const btn = buildBtn();
        startPulse(btn);
        sync();
        // Poll every 400 ms — works across Streamlit re-renders
        setInterval(sync, 400);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
</script>
"""


# ─────────────────────────────────────────────────
# Ollama helpers
# ─────────────────────────────────────────────────

def get_ollama_models() -> list[str]:
    """Return list of locally installed Ollama model names."""
    try:
        import ollama
        result = ollama.list()
        # SDK returns an object with .models list
        models = result.models if hasattr(result, "models") else result.get("models", [])
        names = []
        for m in models:
            if hasattr(m, "model"):
                names.append(m.model)
            elif isinstance(m, dict):
                names.append(m.get("model") or m.get("name", "unknown"))
        return names if names else ["(nenhum modelo encontrado)"]
    except Exception:
        return []


def stream_ollama_response(model: str, messages: list[dict]):
    """Generator that yields text chunks from Ollama streaming chat."""
    try:
        import ollama
        stream = ollama.chat(model=model, messages=messages, stream=True)
        for chunk in stream:
            delta = chunk.message.content if hasattr(chunk, "message") else ""
            if delta:
                yield delta
    except Exception as e:
        yield f"\n\n⚠️ Erro ao comunicar com Ollama: {e}"


# ─────────────────────────────────────────────────
# PDF helper
# ─────────────────────────────────────────────────

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract all text from a PDF given its raw bytes."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [doc[i].get_text() for i in range(len(doc))]
        doc.close()
        return "\n\n".join(pages).strip()
    except Exception as e:
        return f"[Erro ao ler PDF: {e}]"


# ─────────────────────────────────────────────────
# Session-state initialisation
# ─────────────────────────────────────────────────

def init_state():
    if "anon_id" not in st.session_state:
        st.session_state.anon_id = str(uuid.uuid4())[:8]

    # conversations: dict[conv_id] -> {"title": str, "messages": list[dict]}
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}

    # active conversation id
    if "active_conv" not in st.session_state:
        _new_conv()

    # pending PDF context
    if "pdf_context" not in st.session_state:
        st.session_state.pdf_context = None
    if "pdf_name" not in st.session_state:
        st.session_state.pdf_name = None


def _new_conv() -> str:
    cid = str(uuid.uuid4())
    st.session_state.conversations[cid] = {
        "title": "Nova conversa",
        "messages": [],
    }
    st.session_state.active_conv = cid
    st.session_state.pdf_context = None
    st.session_state.pdf_name = None
    return cid


def current_messages() -> list[dict]:
    return st.session_state.conversations[st.session_state.active_conv]["messages"]


# ─────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────

def render_sidebar(models: list[str]) -> str | None:
    """Renders the sidebar and returns the selected model."""
    with st.sidebar:
        # Brand mini
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:1rem;">
                <span style="font-family:'Outfit',sans-serif;font-size:1.3rem;font-weight:900;
                background:linear-gradient(135deg,#c4b5fd,#7c3aed);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">🧘 GuruGPT</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # New chat button
        if st.button("➕  Nova Conversa", key="new_chat_btn"):
            _new_conv()
            st.rerun()

        st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)

        # Conversation history
        st.markdown("<div class='sidebar-title'>Histórico</div>", unsafe_allow_html=True)

        convs = st.session_state.conversations
        active = st.session_state.active_conv

        if not convs:
            st.markdown(
                "<p style='color:#a89fd0;font-size:0.8rem;text-align:center;'>Nenhuma conversa ainda.</p>",
                unsafe_allow_html=True,
            )
        else:
            for cid, conv in list(convs.items()):
                is_active = cid == active
                title = conv["title"]
                icon = "💬" if is_active else "🗨️"

                col1, col2 = st.columns([5, 1])
                with col1:
                    css_class = "conv-item active" if is_active else "conv-item"
                    if st.button(
                        f"{icon} {title}",
                        key=f"conv_{cid}",
                        help=title,
                        use_container_width=True,
                    ):
                        st.session_state.active_conv = cid
                        st.session_state.pdf_context = None
                        st.session_state.pdf_name = None
                        st.rerun()

                with col2:
                    with st.container():
                        st.markdown("<div class='delete-btn'>", unsafe_allow_html=True)
                        if st.button("🗑", key=f"del_{cid}", help="Apagar conversa"):
                            del st.session_state.conversations[cid]
                            if cid == active:
                                if st.session_state.conversations:
                                    st.session_state.active_conv = list(
                                        st.session_state.conversations.keys()
                                    )[-1]
                                else:
                                    _new_conv()
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)

        # Session info
        st.markdown(
            f"<p style='font-size:0.72rem;color:#6b6a8a;text-align:center;'>Sessão anônima · {st.session_state.anon_id}</p>",
            unsafe_allow_html=True,
        )

        # Model selector inside sidebar
        st.markdown("<div class='sidebar-title' style='margin-top:0.5rem;'>Modelo de IA</div>", unsafe_allow_html=True)
        if models:
            selected_model = st.selectbox(
                label="modelo",
                options=models,
                label_visibility="collapsed",
                key="selected_model",
            )
        else:
            st.warning("Ollama não encontrado ou sem modelos instalados.")
            selected_model = None

        return selected_model


# ─────────────────────────────────────────────────
# Main content
# ─────────────────────────────────────────────────

def render_logo(models: list[str]):
    """Renders the centered GuruGPT logo and status."""
    st.markdown(
        """
        <div class="gurugpt-logo">
            <div class="icon-wrap">🧘</div>
            <h1>GuruGPT</h1>
            <p>Seu Chatbot Zen</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Online/offline indicator
    if models:
        st.markdown(
            f"""
            <div class="status-bar" style="justify-content:center;">
                <div class="status-dot"></div>
                <span>Modelo online · {len(models)} disponível{'is' if len(models)!=1 else ''}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="status-bar" style="justify-content:center;">
                <div class="status-dot offline"></div>
                <span>Modelo offline — nenhum modelo detectado</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)


def render_pdf_uploader():
    """Renders the PDF uploader and processes any uploaded file."""
    with st.expander("📄 Anexar PDF para análise", expanded=bool(st.session_state.pdf_name)):
        uploaded = st.file_uploader(
            "Selecione um arquivo PDF",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            if uploaded.name != st.session_state.pdf_name:
                with st.spinner("Extraindo texto do PDF..."):
                    text = extract_pdf_text(uploaded.read())
                st.session_state.pdf_context = text
                st.session_state.pdf_name = uploaded.name
                st.success(f"✅ PDF carregado: **{uploaded.name}** — {len(text):,} caracteres extraídos.")

        if st.session_state.pdf_name:
            st.markdown(
                f"<div class='pdf-badge'>📎 {st.session_state.pdf_name}</div>",
                unsafe_allow_html=True,
            )
            if st.button("❌ Remover PDF", key="remove_pdf"):
                st.session_state.pdf_context = None
                st.session_state.pdf_name = None
                st.rerun()


def render_chat(selected_model: str | None):
    """Renders chat history and handles user input."""
    messages = current_messages()

    # Display existing messages
    for msg in messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🧘"):
            st.markdown(msg["content"])

    # Input
    placeholder = (
        "Digite sua mensagem…" if selected_model else "⚠️ Selecione um modelo para começar"
    )
    prompt = st.chat_input(placeholder, disabled=(not selected_model))

    if prompt and selected_model:
        # Build context-aware messages list
        api_messages = []

        # System prompt enriched with PDF context if present
        system_content = (
            "Você é o GuruGPT, um assistente de IA sábio, claro e útil. "
            "Responda sempre de forma organizada e em português, salvo quando o usuário escrever em outro idioma."
        )
        if st.session_state.pdf_context:
            system_content += (
                f"\n\nO usuário anexou o seguinte documento PDF ({st.session_state.pdf_name}) "
                "para contexto:\n\n"
                + st.session_state.pdf_context[:12000]  # cap at ~12k chars to stay within context
                + ("\n\n[... documento truncado para caber no contexto ...]"
                   if len(st.session_state.pdf_context) > 12000 else "")
            )

        api_messages.append({"role": "system", "content": system_content})
        api_messages.extend(messages)
        api_messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # Store in history
        conv = st.session_state.conversations[st.session_state.active_conv]
        conv["messages"].append({"role": "user", "content": prompt})

        # Auto-title conversation from first user message
        if conv["title"] == "Nova conversa":
            conv["title"] = prompt[:42] + ("…" if len(prompt) > 42 else "")

        # Stream assistant response
        with st.chat_message("assistant", avatar="🧘"):
            response_placeholder = st.empty()
            full_response = ""
            with st.spinner(""):
                for chunk in stream_ollama_response(selected_model, api_messages):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        conv["messages"].append({"role": "assistant", "content": full_response})
        st.rerun()


# ─────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Force sidebar always open: clear Streamlit's cached collapsed state
    st.markdown("""
    <script>
    (function() {
        // Clear any stored sidebar-collapsed state
        try {
            Object.keys(localStorage).forEach(function(k) {
                if (k.toLowerCase().includes('sidebar') || k.toLowerCase().includes('collapsed')) {
                    localStorage.removeItem(k);
                }
            });
        } catch(e) {}

        // If sidebar appears closed, click the expand control
        function forceOpen() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            var w = sidebar.getBoundingClientRect().width;
            if (w < 60) {
                var btn = document.querySelector('[data-testid="collapsedControl"] button')
                       || document.querySelector('[data-testid="collapsedControl"]');
                if (btn) btn.click();
            }
        }

        // Try immediately and after short delays
        forceOpen();
        setTimeout(forceOpen, 200);
        setTimeout(forceOpen, 600);
        setTimeout(forceOpen, 1200);
    })();
    </script>
    """, unsafe_allow_html=True)

    init_state()

    # Fetch models once per run (fast, local call)
    models = get_ollama_models()

    # ── Sidebar ──
    selected_model = render_sidebar(models)

    # ── Main ──
    render_logo(models)
    render_pdf_uploader()
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    render_chat(selected_model)

    # ── Footer ──
    st.markdown(
        """
        <div class="gurugpt-footer">
            GuruGPT&copy; 2026 &mdash; Desenvolvido com <span>&#10084;&#65039;</span> por Marcos Dias.
        </div>
        """,
        unsafe_allow_html=True,
    )



if __name__ == "__main__":
    main()
