"""
GuruGPT — Streamlit AI Chatbot with Ollama
Anonymous multi-session chatbot with PDF analysis and conversation history.
"""

import uuid
import time
import streamlit as st
import streamlit.components.v1 as components
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
    resize: none;
    overflow: hidden;
    min-width: 220px !important;
    max-width: 260px !important;
    width: 260px !important;
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

/* Botão ☰ e backdrop mobile — ocultos por padrão (desktop); @media mobile os reexibe */
#mobile-menu-btn { display: none !important; }
#mobile-sidebar-backdrop { display: none; }


/* ═══════════════════════════════════════════════════
   RESPONSIVIDADE MOBILE  (≤ 768 px)
   ═══════════════════════════════════════════════════ */
@media (max-width: 768px) {

    /* ── Sidebar vira overlay deslizante ── */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100dvh !important;
        width: 82vw !important;
        min-width: unset !important;
        max-width: 320px !important;
        z-index: 9999 !important;
        transform: translateX(-100%) !important;
        transition: transform 0.28s cubic-bezier(.4,0,.2,1) !important;
        resize: none !important;
        box-shadow: 4px 0 32px rgba(0,0,0,0.65);
        overflow-y: auto !important;
        translate: none !important; /* override do CSS desktop */
    }

    [data-testid="stSidebar"].mobile-open {
        transform: translateX(0) !important;
    }

    /* Backdrop escuro atrás do menu */
    #mobile-sidebar-backdrop {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.55);
        z-index: 9998;
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
    }
    #mobile-sidebar-backdrop.visible { display: block; }

    /* Botão ☰ flutuante para abrir o menu */
    #mobile-menu-btn {
        display: flex !important;
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 10000;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        font-size: 1.3rem;
        border: none;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(124,58,237,0.55);
        transition: transform 0.15s ease;
        -webkit-tap-highlight-color: transparent;
    }
    #mobile-menu-btn:active { transform: scale(0.9); }

    /* Área principal — sem margem do sidebar */
    [data-testid="stMain"] {
        margin-left: 0 !important;
        width: 100vw !important;
    }

    [data-testid="stMain"] .block-container {
        padding: 4.2rem 0.75rem 5rem !important;
        max-width: 100% !important;
    }

    /* Logo compacta */
    .gurugpt-logo { padding: 0.4rem 0 0.2rem; }
    .gurugpt-logo .icon-wrap {
        width: 50px; height: 50px;
        font-size: 1.55rem; border-radius: 14px;
        margin-bottom: 7px;
    }
    .gurugpt-logo h1 { font-size: 1.85rem; }
    .gurugpt-logo p  { font-size: 0.76rem; }

    /* Mensagens */
    .stChatMessageContent {
        padding: 0.6rem 0.85rem !important;
        font-size: 0.91rem !important;
    }

    /* Blocos de código — scroll horizontal */
    pre {
        font-size: 0.77rem !important;
        padding: 0.7rem !important;
        border-radius: 8px !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    /* Input de chat */
    [data-testid="stChatInput"] textarea {
        font-size: 1rem !important;
        min-height: 48px !important;
    }

    /* Botões maiores para toque */
    .stButton > button {
        min-height: 44px !important;
        font-size: 0.93rem !important;
    }

    /* Footer compacto */
    .gurugpt-footer {
        font-size: 0.66rem;
        padding: 0.38rem 0.5rem;
    }

    /* Selectbox fullwidth */
    .stSelectbox { width: 100% !important; }

    /* Ocultar botão reabrir sidebar do desktop no mobile */
    #gurugpt-sidebar-open-btn { display: none !important; }
}

/* Telas muito pequenas (≤ 380 px — iPhone SE, Galaxy A) */
@media (max-width: 380px) {
    .gurugpt-logo h1 { font-size: 1.55rem; }
    .gurugpt-logo .icon-wrap { width: 42px; height: 42px; font-size: 1.3rem; }
    [data-testid="stMain"] .block-container { padding: 3.8rem 0.5rem 5rem !important; }
}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# MOBILE ☰ BUTTON — rendered as STATIC HTML (never created by JS)
# Two overlapping spans inside the button: .gg-ham (☰) and .gg-x (✕).
# CSS transitions swap them when #gg-btn has class 'open'.
# ═══════════════════════════════════════════════════════════════
MOBILE_BTN_HTML = (
    '<div id="gg-wrap-2" style="'
    'position:fixed;top:14px;left:14px;z-index:2147483647;'
    'display:none;">'
    '<button id="gg-btn-2" title="Abrir/fechar menu" style="'
    'position:relative;width:48px;height:48px;border-radius:14px;'
    'background:linear-gradient(135deg,#7c3aed,#4f46e5);'
    'color:white;font-size:1.5rem;border:none;cursor:pointer;'
    'display:flex;align-items:center;justify-content:center;'
    'box-shadow:0 4px 24px rgba(124,58,237,0.65);'
    '-webkit-tap-highlight-color:transparent;user-select:none;'
    'overflow:hidden;">'
    # Two layered icons
    '<span class="gg-ham" style="'
    'position:absolute;transition:opacity .25s,transform .25s;'
    'opacity:1;transform:rotate(0deg);">&#9776;</span>'
    '<span class="gg-x" style="'
    'position:absolute;transition:opacity .25s,transform .25s;'
    'opacity:0;transform:rotate(-90deg);font-size:1.2rem;">&#10005;</span>'
    '</button></div>'
    # Backdrop
    '<div id="gg-bd" '
    'style="'
    'display:none;position:fixed;inset:0;'
    'background:rgba(0,0,0,0.55);'
    'backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);'
    'z-index:9997;"></div>'
    # CSS: show/hide + transition
    '<style>'
    '@media(max-width:768px){#gg-wrap-2{display:flex!important;}}'
    '@media(min-width:769px){#gg-wrap-2,#gg-bd{display:none!important;}}'
    # Open state: when body has class 'gg-sidebar-open', swap icons
    'body.gg-sidebar-open #gg-btn-2 .gg-ham{opacity:0!important;transform:rotate(90deg)!important;}'
    'body.gg-sidebar-open #gg-btn-2 .gg-x{opacity:1!important;transform:rotate(0deg)!important;}'
    '#gg-btn-2:active{transform:scale(0.86);}'
    '</style>'
)

# ═══════════════════════════════════════════════════════════════════
# TOGGLE_COMPONENT_HTML — injected via st.components.v1.html(height=0)
#
# Why components.v1.html instead of st.markdown?
#   st.markdown <script> tags: Streamlit re-executes them via createElement
#   but timing with React's rendering is unreliable. The iframe created by
#   components.v1.html() executes scripts synchronously and has same-origin
#   access to window.parent.document (both served from localhost:8501).
#
# Strategy:
#   1. Access parent document from iframe (window.parent)
#   2. Define _ggOpen / _ggClose in the PARENT window scope
#   3. Use MutationObserver on parent.body to detect gg-wrap instantly
#   4. Move gg-wrap + gg-bd to parent.body (escape React's managed tree)
#   5. addEventListener works correctly outside React tree (no Error #231)
#   6. setProperty(prop, val, 'important') overrides all CSS !important rules
# ═══════════════════════════════════════════════════════════════════
TOGGLE_COMPONENT_HTML = """<!DOCTYPE html><html><body style="margin:0;padding:0;overflow:hidden">
<script>
(function(){
  var P  = window.parent;        /* Parent window (main Streamlit page)  */
  var PD = P.document;           /* Parent document                      */
  var PB = PD.body;              /* Parent body                          */

  /* ── _ggOpen / _ggClose: toggle the drawer ── */
  P._ggOpen = function() {
    var sb = PD.querySelector('[data-testid="stSidebar"]');
    /* Toggle: if already open → close */
    if (sb && sb.classList.contains('mobile-open')) {
      P._ggClose();
      return;
    }
    if (sb) {
      sb.classList.add('mobile-open');
      [['position','fixed'],['top','0'],['left','0'],['width','82vw'],
       ['max-width','320px'],['height','100dvh'],['transform','translateX(0)'],
       ['translate','none'],['display','flex'],['visibility','visible'],
       ['opacity','1'],['z-index','99999'],['overflow-y','auto']
      ].forEach(function(p){ sb.style.setProperty(p[0],p[1],'important'); });
    }
    /* Animate button ☰ → ✕ (by adding class to BODY, persistent across re-renders) */
    if (PD.body) PD.body.classList.add('gg-sidebar-open');
    var bd = PD.getElementById('gg-bd');
    if (bd) bd.style.display = 'block';
  };
  P._ggClose = function() {
    var sb = PD.querySelector('[data-testid="stSidebar"]');
    if (sb) {
      sb.classList.remove('mobile-open');
      ['position','top','left','width','max-width','height','transform',
       'translate','display','visibility','opacity','z-index','overflow-y'
      ].forEach(function(p){ sb.style.removeProperty(p); });
    }
    /* Animate button ✕ → ☰ */
    if (PD.body) PD.body.classList.remove('gg-sidebar-open');
    var bd = PD.getElementById('gg-bd');
    if (bd) bd.style.display = 'none';
  };

  /* ── Adopt button + backdrop: move to parent.body, attach handlers ── */
  var _btnReady = false;
  function adoptBtn() {
    if (_btnReady) return;
    var wrap = PD.getElementById('gg-wrap-2');
    var btn  = PD.getElementById('gg-btn-2');
    var bd   = PD.getElementById('gg-bd');
    if (!wrap || !btn) return;

    /* Move elements out of React's managed tree */
    if (wrap.parentElement !== PB) PB.appendChild(wrap);
    if (bd && bd.parentElement !== PB) PB.appendChild(bd);

    /* Attach click handlers (safe outside React tree) */
    btn.addEventListener('click', P._ggOpen);
    if (bd) bd.addEventListener('click', P._ggClose);

    /* Swipe left → close */
    var tx = 0;
    PD.addEventListener('touchstart',function(e){tx=e.changedTouches[0].screenX;},{passive:true});
    PD.addEventListener('touchend',function(e){
      if(e.changedTouches[0].screenX-tx<-60) P._ggClose();
    },{passive:true});

    _btnReady = true;
  }

  /* MutationObserver: fires the instant gg-wrap appears in the DOM */
  var obs = new MutationObserver(function(){ adoptBtn(); });
  obs.observe(PB, {childList:true, subtree:true});
  adoptBtn(); /* also try immediately in case already in DOM */

  /* ── Desktop floating reopen button ── */
  var DESK_ID = 'gurugpt-sidebar-open-btn';
  function ensureDesktop() {
    var b = PD.getElementById(DESK_ID);
    if (!b) {
      b = PD.createElement('button');
      b.id = DESK_ID;
      b.title = 'Abrir painel lateral';
      b.innerHTML = '&#9776;';
      Object.assign(b.style, {
        position:'fixed', top:'50vh', left:'0',
        transform:'translateY(-50%)', zIndex:'2147483646',
        background:'linear-gradient(180deg,#7c3aed,#4f46e5)',
        color:'white', border:'none', borderRadius:'0 14px 14px 0',
        width:'40px', height:'56px', fontSize:'1.2rem',
        cursor:'pointer', display:'none',
        alignItems:'center', justifyContent:'center',
        boxShadow:'4px 0 24px rgba(124,58,237,0.75)',
        transition:'width .2s', fontFamily:'sans-serif', lineHeight:'1',
      });
      b.addEventListener('mouseenter',function(){b.style.width='50px';});
      b.addEventListener('mouseleave',function(){b.style.width='40px';});
      b.addEventListener('click',function(){
        var t = PD.querySelector('[data-testid="collapsedControl"] button')
             || PD.querySelector('[data-testid="stSidebarCollapseButton"] button');
        if (t) t.click();
      });
      PB.appendChild(b);
      var pt=0;
      setInterval(function(){
        pt+=0.05;
        var g=0.55+0.3*Math.sin(pt);
        b.style.boxShadow='4px 0 '+Math.round(20+16*Math.sin(pt))+'px rgba(124,58,237,'+g.toFixed(2)+')';
      },50);
    }
    if (P.innerWidth<=768){b.style.display='none';return;}
    var sb=PD.querySelector('[data-testid="stSidebar"]');
    b.style.display=(sb&&sb.getBoundingClientRect().width>60)?'none':'flex';
  }
  ensureDesktop();
  setTimeout(ensureDesktop,400);
  setInterval(ensureDesktop,1500);
  P.addEventListener('resize',ensureDesktop);
})();
</script>
</body></html>"""




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
                background-clip:text;">&#129368; GuruGPT</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Styles for conversation rows (title + X as one visual unit)
        st.markdown(
            """
            <style>
            /* Nova Conversa centralizado */
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:first-of-type {
                text-align: center !important;
                justify-content: center !important;
            }
            /* Conversation rows: force single-line flex layout on mobile */
            .conv-row [data-testid="stHorizontalBlock"] {
                gap: 0 !important;
                margin-bottom: 5px !important;
                flex-wrap: nowrap !important;
                align-items: stretch !important;
            }
            .conv-row [data-testid="stColumn"] {
                min-width: 0 !important;
                flex-shrink: 1 !important;
            }
            .conv-row [data-testid="stColumn"]:last-child {
                flex: 0 0 auto !important;
                width: auto !important;
            }
            /* Title button: left side pill */
            .conv-row [data-testid="column"]:first-child button,
            .conv-row [data-testid="stColumn"]:first-child button {
                border-radius: 10px 0 0 10px !important;
                text-align: left !important;
                border-right: 1px solid rgba(124,58,237,0.2) !important;
            }
            /* X button: right side pill */
            .conv-row [data-testid="column"]:last-child button,
            .conv-row [data-testid="stColumn"]:last-child button {
                border-radius: 0 10px 10px 0 !important;
                background: transparent !important;
                color: #6b6a8a !important;
                font-weight: 500 !important;
                font-size: 0.65rem !important;
                letter-spacing: 0 !important;
                box-shadow: none !important;
                padding: 0 6px !important;
                height: 100% !important;
                min-height: 0 !important;
                line-height: 1.2 !important;
                white-space: nowrap !important;
                overflow: hidden !important;
            }
            .conv-row [data-testid="column"]:last-child button:hover,
            .conv-row [data-testid="stColumn"]:last-child button:hover {
                background: rgba(239,68,68,0.18) !important;
                color: #ef4444 !important;
                transform: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # New chat button
        if st.button("\u2795\u2009 Nova Conversa", key="new_chat_btn", use_container_width=True):
            _new_conv()
            st.rerun()

        st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)

        # Conversation history
        st.markdown("<div class='sidebar-title'>Hist\u00f3rico</div>", unsafe_allow_html=True)

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
                icon = "\U0001f4ac" if is_active else "\U0001f5e8\ufe0f"

                st.markdown("<div class='conv-row'>", unsafe_allow_html=True)
                col_t, col_x = st.columns([8, 1])

                with col_t:
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

                with col_x:
                    if st.button("×", key=f"del_{cid}", help="Apagar conversa", use_container_width=True):
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
            f"<p style='font-size:0.72rem;color:#6b6a8a;text-align:center;'>Sess\u00e3o an\u00f4nima \u00b7 {st.session_state.anon_id}</p>",
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
            st.warning("Ollama n\u00e3o encontrado ou sem modelos instalados.")
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
            "Responda sempre de forma organizada e em português, salvo quando o usuário escrever em outro idioma.\n\n"
            "Regras de formatação obrigatórias:\n"
            "- Sempre que incluir código-fonte (em qualquer linguagem), envolva-o em um bloco Markdown com o identificador da linguagem. "
            "Exemplo: use ```python ... ``` para Python, ```javascript ... ``` para JavaScript, ```java ... ``` para Java, etc.\n"
            "- Nunca exiba código como texto simples ou dentro de parágrafos.\n"
            "- Use títulos (##), listas e negrito (**texto**) para organizar explicações longas."
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
                    # Count backtick-fence openings to detect if we're inside a code block.
                    # An odd number of ``` in the response means a block is still open.
                    open_fences = full_response.count("```") % 2 == 1
                    if open_fences:
                        # Close the fence temporarily so Markdown renders correctly,
                        # then show the cursor on a new line outside the block.
                        response_placeholder.markdown(full_response + "\n```\n\n▌")
                    else:
                        response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        conv["messages"].append({"role": "assistant", "content": full_response})
        st.rerun()


# ─────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    # ☰ button: STATIC HTML — always in DOM, no JS needed to create it
    st.markdown(MOBILE_BTN_HTML, unsafe_allow_html=True)
    # JS via iframe (components.v1.html guarantees script execution):
    # accesses window.parent.document, moves button out of React tree,
    # attaches addEventListener safely outside React's managed DOM.
    components.html(TOGGLE_COMPONENT_HTML, height=0)

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
