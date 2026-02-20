```markdown
# 🧘 GuruGPT – Chatbot IA com Streamlit + Ollama

GuruGPT é um **chatbot multilinhas anônimo** com interface em Streamlit, integração com modelos locais via **Ollama** e suporte a **análise de PDFs** usando PyMuPDF.  
O foco é oferecer uma experiência de chat “zen”, com múltiplas conversas, histórico e contexto de documentos.

---

## ✨ Features

- 💬 Chat em múltiplas conversas (multi‑sessions) com histórico por sessão.
- 🧠 Integração com **Ollama** para uso de modelos LLM locais.
- 📄 Upload e leitura de **PDFs** com extração de texto via PyMuPDF.
- 🕶️ Tema escuro customizado e layout wide em Streamlit.
- 🧾 Controle de estado via `st.session_state` (ID anônimo, conversas, PDF em uso).
- 🧱 Sidebar com:
  - Lista de conversas
  - Seleção de modelo Ollama
  - Identificador anônimo da sessão

---

## 🧩 Arquitetura do Projeto

Principais tecnologias:

- [Streamlit](https://streamlit.io/) – UI web.
- [Ollama](https://ollama.com/) – Modelos LLM locais.
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) – Leitura e extração de texto de PDFs.
- Python 3.12+ (recomendado em venv).

### Estrutura básica

```text
.
├── app.py            # App Streamlit principal
├── requirements.txt  # Dependências de Python
└── (outros arquivos e configs)
```


### Principais componentes do `app.py`

- `get_ollama_models()`
Lista os modelos instalados localmente no Ollama e exibe no seletor da sidebar.
- `stream_ollama_response(model, messages)`
Faz streaming da resposta do Ollama, chunk a chunk, para o chat do usuário.
- `extract_pdf_text(file_bytes)`
Lê um PDF enviado pelo usuário e extrai todo o texto usando PyMuPDF.
- `init_state()` / `_new_conv()` / `current_messages()`
Gerenciam o estado da sessão: ID anônimo, conversas, conversa ativa e contexto de PDF.
- `render_sidebar(models)`
Monta a sidebar com:
    - Logo / branding
    - Lista de conversas
    - Seleção de modelo Ollama
    - Info da sessão anônima
- `render_logo(models)`
Renderiza o logo “GuruGPT” e mensagens de status na tela principal.

---

## 📦 Dependências

Do arquivo `requirements.txt`:

```txt
streamlit>=1.32.0
ollama>=0.1.8
PyMuPDF>=1.23.0
```


---

## 🚀 Como rodar localmente (Linux)

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/gurugpt.git
cd gurugpt
```


### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> ⚠️ Isso evita o erro `externally-managed-environment` do pip (PEP 668) ao instalar pacotes no Python do sistema.

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```


### 4. Instalar e configurar o Ollama

- Instale o Ollama no seu sistema (veja docs oficiais: https://ollama.com).
- Puxe pelo menos um modelo (por exemplo, `llama3`):

```bash
ollama pull llama3
```

- Certifique-se de que o serviço do Ollama está rodando antes de iniciar o GuruGPT.


### 5. Rodar o app Streamlit

Por padrão, o Streamlit roda na porta `8501`:

```bash
streamlit run app.py
```

Abra no navegador:

```text
http://localhost:8501
```


### 6. Escolher outra porta (opcional)

```bash
streamlit run app.py --server.port=8502
```

Ou configure no arquivo `.streamlit/config.toml`:

```toml
[server]
port = 8502
```


---

## 🌐 Deploy com NGINX (reverse proxy)

Abaixo um exemplo de como publicar o GuruGPT na web usando **NGINX como proxy reverso**.

### 1. Rodar o Streamlit em background

Exemplo rodando na porta `8501`:

```bash
cd /var/www/gurugpt.com.br
source .venv/bin/activate
streamlit run app.py --server.port=8501
```

Você pode usar `tmux`, `screen` ou um serviço `systemd` para manter o processo rodando.

### 2. Configurar o NGINX

Crie um arquivo de site, por exemplo:

```bash
sudo nano /etc/nginx/sites-available/gurugpt.com.br
```

Com o conteúdo:

```nginx
server {
    listen 80;
    server_name gurugpt.com.br www.gurugpt.com.br;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```


### 3. Habilitar o site e recarregar o NGINX

```bash
sudo ln -s /etc/nginx/sites-available/gurugpt.com.br /etc/nginx/sites-enabled/gurugpt.com.br

sudo nginx -t      # testa a configuração
sudo systemctl reload nginx
```

Certifique-se de que seu DNS (`A` ou `AAAA`) aponta `gurugpt.com.br` para o IP do servidor.

### 4. HTTPS com Certbot (opcional, recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d gurugpt.com.br -d www.gurugpt.com.br
```

Isso irá:

- Gerar certificados TLS.
- Configurar redirecionamento HTTP → HTTPS automaticamente.

---

## 🧪 Uso básico

1. Acesse o endereço do app (local ou domínio).
2. Escolha um modelo Ollama na sidebar.
3. Envie mensagens no chat.
4. (Opcional) Faça upload de um PDF para que o modelo use o conteúdo como contexto.
5. Crie novas conversas pela sidebar para separar assuntos.

---

## 🛠️ Roadmap / Ideias futuras

- 📚 Suporte a múltiplos arquivos e tipos (DOCX, TXT etc.).
- 💾 Persistência de histórico em banco (SQLite/Postgres).
- 👤 Autenticação de usuários.
- 🌐 Seleção de modelo remoto (APIs externas).

---

## 🤝 Contribuições

Pull requests, issues e sugestões são bem-vindas!
Sinta-se à vontade para abrir uma issue com ideias de melhoria ou bugs encontrados.

---
## 📜 Licença

GPL-3.0 license
