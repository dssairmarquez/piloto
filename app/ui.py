PAGE_HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>MiniGPT Projects</title>
  <style>
    :root{
      --bg:#0b0f17;
      --panel:#111827;
      --muted:#94a3b8;
      --text:#e5e7eb;
      --line:#1f2937;
      --accent:#60a5fa;
      --good:#34d399;
      --bad:#fb7185;
      --warn:#fbbf24;
      --r:14px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: var(--bg);
      color: var(--text);
    }
    .wrap{ max-width: 1320px; margin: 0 auto; padding: 14px; }

    header{
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      padding: 10px 12px; border: 1px solid var(--line); border-radius: var(--r);
      background: rgba(17,24,39,.92); position: sticky; top: 10px; z-index: 10;
      backdrop-filter: blur(10px);
    }
    header .left{ display:flex; align-items:center; gap:10px; min-width: 0; }
    header h1{ margin:0; font-size: 14px; letter-spacing:.2px; white-space:nowrap; }
    header .pill{ font-size: 12px; color: var(--muted); white-space:nowrap; }

    .layout{
      margin-top: 12px;
      display:grid;
      grid-template-columns: 360px 1fr;
      gap: 12px;
      min-height: calc(100vh - 90px);
    }
    @media(max-width: 980px){ .layout{ grid-template-columns: 1fr; } }

    .panel{
      border: 1px solid var(--line); border-radius: var(--r);
      background: rgba(17,24,39,.92); overflow:hidden; min-height: 120px;
    }
    .panel .hd{
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      padding: 10px 12px; border-bottom: 1px solid var(--line);
    }
    .panel .hd .title{
      font-size: 12px; text-transform: uppercase; letter-spacing: .9px;
      color: var(--muted); font-weight: 700;
    }
    .panel .bd{ padding: 10px 12px; }

    input, textarea, select{
      width:100%; padding: 10px 10px; border-radius: 12px;
      border: 1px solid var(--line); background: #0b1220; color: var(--text); outline:none;
    }
    textarea{ resize: vertical; min-height: 52px; }

    .row{ display:flex; gap: 8px; align-items:center; }
    .col{ display:flex; flex-direction:column; gap: 10px; }

    button{
      padding: 10px 12px; border-radius: 12px; border: 1px solid var(--line);
      background: transparent; color: var(--text); cursor:pointer;
      transition: border-color .15s ease, transform .08s ease, opacity .15s ease;
      user-select:none; white-space:nowrap;
    }
    button:hover{ transform: translateY(-1px); border-color: rgba(96,165,250,.55); }
    button:disabled{ opacity:.5; cursor:not-allowed; transform:none; }
    .btn-accent{ border-color: rgba(96,165,250,.45); }
    .btn-good{ border-color: rgba(52,211,153,.45); }
    .btn-bad{ border-color: rgba(251,113,133,.45); }
    .btn-ghost{ opacity: .85; }
    .btn-ghost:hover{ opacity: 1; }

    .hint{ font-size: 12px; color: var(--muted); margin-top: 6px; }

    /* Sidebar tree */
    .treewrap{
      height: calc(100vh - 230px);
      overflow:auto;
      padding-right: 2px;
      display:flex;
      flex-direction:column;
      gap: 8px;
    }
    @media(max-width: 980px){ .treewrap{ height: 320px; } }

    .node{
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(11,18,32,.65);
      overflow:hidden;
    }
    .node-hd{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap: 10px;
      padding: 10px;
      cursor:pointer;
    }
    .node-hd:hover{ background: rgba(96,165,250,.06); }
    .node-hd.sel{ outline: 1px solid rgba(96,165,250,.55); }

    .node-left{ min-width:0; display:flex; gap:10px; align-items:flex-start; }
    .caret{
      width: 18px; height: 18px; display:grid; place-items:center;
      border: 1px solid var(--line); border-radius: 8px;
      font-size: 12px; color: var(--muted);
      background: rgba(0,0,0,.18);
      margin-top: 1px;
      flex: 0 0 auto;
    }
    .node-title{
      font-weight: 800; font-size: 13px; line-height: 1.2;
      word-break: break-word;
    }
    .node-meta{ font-size: 12px; color: var(--muted); margin-top: 2px; }
    .node-actions{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; justify-content:flex-end; }
    .iconbtn{
      padding: 8px 10px;
      border-radius: 10px;
      font-size: 12px;
    }

    .children{
      border-top: 1px solid var(--line);
      background: rgba(11,18,32,.35);
      padding: 8px;
      display:flex;
      flex-direction:column;
      gap: 6px;
    }
    .child{
      border: 1px solid rgba(31,41,55,.9);
      border-radius: 12px;
      padding: 9px 10px;
      background: rgba(11,18,32,.55);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap: 10px;
      cursor:pointer;
    }
    .child:hover{ background: rgba(52,211,153,.06); }
    .child.sel{ outline: 1px solid rgba(52,211,153,.55); }

    .child .name{
      font-weight: 800; font-size: 13px; min-width:0;
      overflow:hidden; text-overflow: ellipsis; white-space:nowrap;
    }
    .child .meta{ font-size: 12px; color: var(--muted); margin-top: 2px; }
    .child .left{ min-width:0; display:flex; flex-direction:column; }
    .child .right{ display:flex; gap: 8px; align-items:center; }

    /* Main workspace */
    .workspace{ display:flex; flex-direction:column; gap: 12px; }
    .topbar{
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      padding: 10px 12px; border: 1px solid var(--line); border-radius: var(--r);
      background: rgba(17,24,39,.92);
    }
    .topbar .project{
      font-weight: 800; font-size: 14px; min-width: 0;
      overflow:hidden; text-overflow: ellipsis; white-space:nowrap;
    }
    .topbar .actions{ display:flex; gap: 8px; align-items:center; flex-wrap: wrap; justify-content:flex-end; }

    .badge{
      font-size: 12px; color: var(--muted); border: 1px solid var(--line);
      padding: 6px 10px; border-radius: 999px; background: rgba(11,18,32,.55);
      white-space:nowrap;
    }
    .badge.good{ color: var(--good); border-color: rgba(52,211,153,.35); }
    .badge.muted{ color: var(--muted); }

    .chatpanel{
      border: 1px solid var(--line); border-radius: var(--r);
      background: rgba(17,24,39,.92); overflow:hidden;
      display:flex; flex-direction:column; min-height: 560px;
    }
    .chatpanel .hd{
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      padding: 10px 12px; border-bottom: 1px solid var(--line);
    }
    .chatpanel .hd .ctitle{
      font-weight: 800; font-size: 13px; color: var(--text);
      min-width: 0; overflow:hidden; text-overflow: ellipsis; white-space:nowrap;
    }

    .chatbox{
      flex: 1;
      overflow:auto;
      padding: 12px;
      display:flex;
      flex-direction:column;
      gap: 10px;
      background: rgba(11,18,32,.55);
      scroll-behavior: smooth;
    }
    .bubble{
      max-width: 92%;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      line-height: 1.35;
      font-size: 14px;
    }
    .bubble.user{
      align-self:flex-end; border-color: rgba(96,165,250,.35);
      background: rgba(96,165,250,.10);
    }
    .bubble.assistant{
      white-space: pre-wrap;
      align-self:flex-start; background: rgba(148,163,184,.08);
    }

    /* “Paso” (evento) */
    .bubble.event{
      align-self:flex-start;
      border-style: dashed;
      background: rgba(251,191,36,.06);
      border-color: rgba(251,191,36,.35);
    }
    .bubble.event.good{
      background: rgba(52,211,153,.07);
      border-color: rgba(52,211,153,.45);
    }
    .bubble.event.bad{
      background: rgba(251,113,133,.07);
      border-color: rgba(251,113,133,.45);
    }

    /* Bloques tipo ```bash ...``` (simple + limpio) */
    .cmdblock{
      margin-top: 8px;
      border: 1px solid rgba(148,163,184,.22);
      border-radius: 12px;
      overflow:hidden;
      background: rgba(0,0,0,.22);
    }
    .cmdblock .lang{
      font-size: 11px;
      color: var(--muted);
      padding: 6px 10px;
      border-bottom: 1px solid rgba(148,163,184,.15);
      background: rgba(0,0,0,.18);
      letter-spacing: .6px;
      text-transform: uppercase;
    }
    .cmdblock pre{
      margin: 0;
      padding: 10px 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12.5px;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.35;
    }
    .cmdblock.out pre{ opacity: .95; }

    .composer{ border-top: 1px solid var(--line); padding: 10px 12px; background: rgba(17,24,39,.92); }
    .composer .row{ align-items:flex-end; }
    .composer textarea{ min-height: 56px; max-height: 180px; }

    .toast{
      position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
      background: rgba(17,24,39,.95); border: 1px solid var(--line);
      color: var(--text); padding: 10px 12px; border-radius: 999px;
      font-size: 13px; opacity: 0; pointer-events:none;
      transition: opacity .15s ease; max-width: 92vw; z-index: 50;
    }
    .toast.show{ opacity: 1; }

    /* Modal */
    .modal-backdrop{
      position: fixed; inset: 0; background: rgba(0,0,0,.55);
      display:none; align-items:center; justify-content:center; z-index: 40; padding: 16px;
    }
    .modal{
      width: min(1100px, 98vw); max-height: 92vh; overflow:auto;
      border: 1px solid var(--line); border-radius: 16px; background: rgba(17,24,39,.96);
    }
    .modal .mhd{
      padding: 10px 12px; border-bottom: 1px solid var(--line);
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      position: sticky; top: 0; background: rgba(17,24,39,.98);
      backdrop-filter: blur(10px); z-index: 1;
    }
    .modal .mbd{ padding: 10px 12px; }
    .split{ display:grid; gap: 12px; grid-template-columns: 1fr 1fr; }
    @media(max-width: 980px){ .split{ grid-template-columns: 1fr; } }
    .toggle{
      display:flex; align-items:flex-start; justify-content:space-between; gap: 10px;
      border: 1px solid var(--line); border-radius: 12px; padding: 10px;
      background: rgba(11,18,32,.60);
    }
    .toggle .left{ display:flex; flex-direction:column; gap: 4px; }
    .toggle .right{ display:flex; flex-wrap: wrap; gap: 8px; align-items:center; justify-content:flex-end; }
    .tag{
      font-size: 11px; padding: 4px 8px; border-radius: 999px;
      border: 1px solid var(--line); color: var(--muted); white-space: nowrap;
    }
    .tag.active{ color: var(--good); border-color: rgba(52,211,153,.35); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="left">
        <h1>MiniGPT Projects</h1>
        <span class="pill" id="statusPill">Listo</span>
      </div>
      <div class="pill">Atajos: Ctrl+K nuevo chat · Ctrl+Enter enviar · Esc cerrar modal</div>
    </header>

    <div class="layout">
      <!-- Sidebar: Tree -->
      <div class="panel">
        <div class="hd">
          <div class="title">Proyectos y chats</div>
          <div class="row">
            <button class="btn-ghost" onclick="refreshAll()">↻</button>
          </div>
        </div>
        <div class="bd col">
          <div class="row">
            <input id="projectName" placeholder="Nombre del proyecto"/>
            <button class="btn-accent" onclick="createProject()">Crear</button>
          </div>

          <div class="treewrap" id="treeList"></div>

          <div class="hint">
            Click en un proyecto: selecciona + toggle. Click en un chat: abre.
          </div>
        </div>
      </div>

      <!-- Main: Workspace -->
      <div class="workspace">
        <div class="topbar">
          <div class="project" id="projectTitle">Selecciona un proyecto</div>
          <div class="actions">
            <span class="badge muted" id="activeContextsPill">0 contextos activos</span>
            <button class="btn-good" onclick="createChat()" title="Nuevo chat">+ Chat</button>
            <button class="btn-accent" onclick="openContextsModal()">Contextos</button>
            <button class="btn-bad" onclick="deleteProject()">Eliminar proyecto</button>
            <button class="btn-ghost" onclick="goHome()">Inicio</button>
          </div>
        </div>

        <div id="emptyPanel" class="hint" style="display:block; padding: 6px 2px;">
          Elige un proyecto a la izquierda para ver sus chats.
        </div>

        <div id="projectPanel" style="display:none;">
          <div class="chatpanel">
            <div class="hd">
              <div class="ctitle" id="chatTitle">Selecciona un chat</div>
            </div>

            <div class="chatbox" id="chatBox"></div>

            <div class="composer">
              <div class="row">
                <textarea id="msgInput" placeholder="Escribe tu mensaje..."></textarea>
                <button id="sendBtn" class="btn-good" onclick="sendMessage()" style="min-width: 110px;">Enviar</button>
              </div>
              <div class="hint">
                Modo agente: verás plan/comandos/output en tiempo real.
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- Contexts Modal -->
  <div class="modal-backdrop" id="ctxModalBackdrop" onclick="modalBackdropClick(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="mhd">
        <div class="row" style="gap:10px;">
          <div style="font-weight:800;">Contextos globales</div>
          <span class="badge" id="ctxModalProjectChip">Proyecto: -</span>
        </div>
        <div class="row">
          <button class="btn-ghost" onclick="closeContextsModal()">Cerrar</button>
        </div>
      </div>
      <div class="mbd">
        <div class="split">
          <!-- Left: contexts -->
          <div class="col">
            <div class="panel">
              <div class="hd"><div class="title">Crear contexto</div></div>
              <div class="bd col">
                <input id="ctxName" placeholder="Nombre (ej: 'Soporte técnico')"/>
                <textarea id="ctxContent" placeholder="Contenido del contexto..."></textarea>
                <div class="row" style="justify-content:flex-end;">
                  <button class="btn-ghost" onclick="fillExampleContext()">Ejemplo</button>
                  <button class="btn-good" onclick="createGlobalContext()">Guardar</button>
                </div>
              </div>
            </div>

            <div class="row" style="justify-content:space-between; margin-top: 8px;">
              <div style="font-weight:800; font-size: 13px;">Activar/desactivar en este proyecto</div>
              <button class="btn-ghost" onclick="reloadProjectContexts()">↻</button>
            </div>

            <div class="treewrap" id="projectContextsList" style="height: auto; max-height: 360px;"></div>
          </div>

          <!-- Right: groups -->
          <div class="col">
            <div class="panel">
              <div class="hd"><div class="title">Grupos</div></div>
              <div class="bd col">
                <div class="row">
                  <input id="groupName" placeholder="Nombre del grupo (ej: 'Ecommerce')"/>
                  <button class="btn-good" onclick="createGroup()">Crear</button>
                </div>

                <div class="treewrap" id="groupsList" style="height: auto; max-height: 240px;"></div>

                <div class="hint">Selecciona un grupo para editar sus contextos.</div>

                <div class="row" style="justify-content:space-between; align-items:center;">
                  <div style="font-weight:800; font-size: 13px;">Editar grupo</div>
                  <span class="badge" id="selectedGroupLabel">(ninguno)</span>
                </div>

                <select id="groupContextsSelect" multiple size="10"></select>

                <div class="row" style="flex-wrap:wrap; justify-content:flex-end;">
                  <button class="btn-ghost" onclick="activateSelectedGroup(false)">Desactivar en proyecto</button>
                  <button class="btn-ghost" onclick="activateSelectedGroup(true)">Activar en proyecto</button>
                  <button class="btn-good" onclick="saveGroupItems()">Guardar grupo</button>
                </div>

                <div class="hint">Tip: Ctrl/Cmd para seleccionar varios.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script>
  let state = {
    selectedProjectId: null,
    selectedChatId: null,
    selectedGroupId: null,
    projects: [],
    chatsByProject: {},      // { [projectId]: { loaded: bool, chats: [] } }
    messages: [],
    projectContexts: [],
    groups: [],
    allContexts: [],
    expandedProjects: new Set()
  };

  const $ = (id) => document.getElementById(id);

  function setStatus(text){ $("statusPill").textContent = text; }

  let toastTimer = null;
  function toast(msg){
    const t = $("toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(()=>t.classList.remove("show"), 2200);
  }

  function disableSend(disabled){
    $("sendBtn").disabled = disabled;
    $("msgInput").disabled = disabled;
  }

  function esc(s){
    return (s ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
  }

  function scrollChatToBottom(){
    const box = $("chatBox");
    box.scrollTop = box.scrollHeight;
  }

  async function api(path, options={}){
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
    if(!res.ok){
      let msg = "Error";
      try{
        const j = await res.json();
        msg = j.detail || JSON.stringify(j);
      }catch(e){
        msg = await res.text();
      }
      throw new Error(msg);
    }
    return res.json();
  }

  function showProjectPanel(show){
    $("projectPanel").style.display = show ? "block" : "none";
    $("emptyPanel").style.display = show ? "none" : "block";
  }

  function getProjectNode(projectId){
    const key = String(projectId);
    if(!state.chatsByProject[key]){
      state.chatsByProject[key] = { loaded: false, chats: [] };
    }
    return state.chatsByProject[key];
  }

  async function ensureChatsLoaded(projectId){
    const node = getProjectNode(projectId);
    if(node.loaded) return;
    node.chats = await api(`/api/projects/${projectId}/chats`);
    node.loaded = true;
  }

  async function refreshProjectChats(projectId){
    const node = getProjectNode(projectId);
    node.chats = await api(`/api/projects/${projectId}/chats`);
    node.loaded = true;
  }

  function renderTree(){
    const list = $("treeList");
    list.innerHTML = "";

    for(const p of state.projects){
      const isSel = (p.id === state.selectedProjectId);
      const isOpen = state.expandedProjects.has(p.id);
      const node = document.createElement("div");
      node.className = "node";

      const hd = document.createElement("div");
      hd.className = "node-hd" + (isSel ? " sel" : "");
      hd.onclick = () => toggleProjectNode(p.id);

      const caret = isOpen ? "▾" : "▸";

      hd.innerHTML = `
        <div class="node-left">
          <div class="caret">${caret}</div>
          <div style="min-width:0;">
            <div class="node-title">${esc(p.name)}</div>
            <div class="node-meta">#${p.id} · ${esc(p.created_at)}</div>
          </div>
        </div>
        <div class="node-actions">
          <button class="btn-ghost iconbtn" title="Actualizar chats" onclick="event.stopPropagation(); reloadProjectChats(${p.id})">↻</button>
        </div>
      `;
      node.appendChild(hd);

      if(isOpen){
        const children = document.createElement("div");
        children.className = "children";

        const projNode = getProjectNode(p.id);
        const chats = projNode.chats || [];

        // hint dentro
        if(!projNode.loaded){
          children.innerHTML = `<div class="hint">Cargando chats…</div>`;
        }else if(chats.length === 0){
          children.innerHTML = `<div class="hint">No hay chats. Crea uno con “+ Chat”.</div>`;
        }else{
          for(const ch of chats){
            const isChatSel = (ch.id === state.selectedChatId);
            const child = document.createElement("div");
            child.className = "child" + (isChatSel ? " sel" : "");
            child.onclick = () => selectChat(ch.id);

            child.innerHTML = `
              <div class="left">
                <div class="name">${esc(ch.title)}</div>
                <div class="meta">#${ch.id} · ${esc(ch.created_at)}</div>
              </div>
              <div class="right">
                <button class="btn-bad iconbtn" title="Eliminar chat" onclick="event.stopPropagation(); deleteChat(${ch.id})">🗑</button>
              </div>
            `;
            children.appendChild(child);
          }
        }

        node.appendChild(children);
      }

      list.appendChild(node);
    }

    if(state.projects.length === 0){
      list.innerHTML = `<div class="hint">No hay proyectos. Crea el primero arriba.</div>`;
    }
  }

  async function toggleProjectNode(projectId){
    const wasOpen = state.expandedProjects.has(projectId);

    // Siempre seleccionar el proyecto al click
    if(state.selectedProjectId !== projectId){
      await selectProject(projectId, { autoExpand: true });
      return;
    }

    // Toggle open/close
    if(wasOpen) state.expandedProjects.delete(projectId);
    else state.expandedProjects.add(projectId);

    // Si abrimos, cargamos chats
    if(!wasOpen){
      try{
        setStatus("Cargando chats…");
        await ensureChatsLoaded(projectId);
      }catch(e){
        toast("Error: " + e.message);
      }finally{
        setStatus("Listo");
      }
    }

    renderTree();
  }

  async function reloadProjectChats(projectId){
    try{
      setStatus("Actualizando chats…");
      await refreshProjectChats(projectId);
      renderTree();
      toast("Chats actualizados");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  function renderMessages(){
    const box = $("chatBox");
    box.innerHTML = "";
    for(const m of state.messages){
      const div = document.createElement("div");
      div.className = "bubble " + (m.role === "user" ? "user" : "assistant");
      div.textContent = m.content;
      box.appendChild(div);
    }
    if(state.messages.length === 0){
      box.innerHTML = `<div class="hint">Escribe un mensaje para empezar.</div>`;
    }
    scrollChatToBottom();
  }

  function renderContextsPreview(){
    const active = state.projectContexts.filter(x => x.is_active === 1);
    const pill = $("activeContextsPill");
    pill.textContent = `${active.length} contextos activos`;
    pill.classList.remove("good");
    pill.classList.remove("muted");
    pill.classList.add(active.length ? "good" : "muted");
  }

  function renderProjectContextsModal(){
    const list = $("projectContextsList");
    list.innerHTML = "";
    for(const c of state.projectContexts){
      const isActive = c.is_active === 1;
      const el = document.createElement("div");
      el.className = "toggle";
      el.innerHTML = `
        <div class="left">
          <div style="font-weight:800;">${esc(c.name)}</div>
          <div class="meta" style="white-space:pre-wrap; color: var(--muted); font-size:12px;">${esc(c.content)}</div>
        </div>
        <div class="right">
          <span class="tag ${isActive ? "active" : ""}">${isActive ? "ACTIVO" : "INACTIVO"}</span>
          <button class="${isActive ? "btn-ghost" : "btn-good"}" onclick="toggleProjectContext(${c.id}, ${isActive ? "false" : "true"})">
            ${isActive ? "Desactivar" : "Activar"}
          </button>
          <button class="btn-bad" onclick="deleteGlobalContext(${c.id})">Borrar</button>
        </div>
      `;
      list.appendChild(el);
    }
    if(state.projectContexts.length === 0){
      list.innerHTML = `<div class="hint">No hay contextos globales todavía. Crea uno arriba.</div>`;
    }
  }

  function renderGroups(){
    const list = $("groupsList");
    list.innerHTML = "";
    for(const g of state.groups){
      const isSel = g.id === state.selectedGroupId;
      const el = document.createElement("div");
      el.className = "node";
      el.innerHTML = `
        <div class="node-hd ${isSel ? "sel" : ""}" onclick="selectGroup(${g.id})">
          <div class="node-left">
            <div class="caret">≡</div>
            <div style="min-width:0;">
              <div class="node-title">${esc(g.name)}</div>
              <div class="node-meta">#${g.id} · ${esc(g.created_at)}</div>
            </div>
          </div>
          <div class="node-actions">
            <button class="btn-bad iconbtn" onclick="event.stopPropagation(); deleteGroup(${g.id})">🗑</button>
          </div>
        </div>
      `;
      list.appendChild(el);
    }
    if(state.groups.length === 0){
      list.innerHTML = `<div class="hint">No hay grupos. Crea el primero arriba.</div>`;
    }
  }

  function renderGroupSelectOptions(){
    const sel = $("groupContextsSelect");
    sel.innerHTML = "";
    for(const c of state.allContexts){
      const opt = document.createElement("option");
      opt.value = String(c.id);
      opt.textContent = `${c.name} (#${c.id})`;
      sel.appendChild(opt);
    }
  }

  async function refreshAll(){
    setStatus("Cargando…");
    try{
      state.projects = await api("/api/projects");

      // Mantener expansión/selección razonable
      // (no tocar expandedProjects si ya existía)
      renderTree();

      if(state.selectedProjectId){
        await loadProject(state.selectedProjectId, { silentTree: true });
      }

      toast("Actualizado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function createProject(){
    const name = $("projectName").value.trim();
    if(!name){ toast("Escribe un nombre"); return; }
    setStatus("Creando…");
    try{
      await api("/api/projects", { method:"POST", body: JSON.stringify({name}) });
      $("projectName").value = "";
      await refreshAll();
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function selectProject(id, opts={ autoExpand:false }){
    state.selectedProjectId = id;
    state.selectedChatId = null;
    state.messages = [];
    $("chatTitle").textContent = "Selecciona un chat";
    renderMessages();

    if(opts.autoExpand){
      state.expandedProjects.add(id);
    }

    await loadProject(id);
  }

  async function loadProject(id, opts={ silentTree:false }){
    setStatus("Cargando proyecto…");
    try{
      const project = await api(`/api/projects/${id}`);
      $("projectTitle").textContent = "Proyecto: " + project.name;
      showProjectPanel(true);

      // cargar chats del proyecto seleccionado
      await ensureChatsLoaded(id);

      // contexts
      state.projectContexts = await api(`/api/projects/${id}/contexts`);
      renderContextsPreview();

      if(!opts.silentTree){
        renderTree();
      }else{
        // aun en silent, si el proyecto seleccionado está expandido, refleja chats
        renderTree();
      }

      toast("Proyecto cargado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  function goHome(){
    state.selectedProjectId = null;
    state.selectedChatId = null;
    $("projectTitle").textContent = "Selecciona un proyecto";
    showProjectPanel(false);
    $("activeContextsPill").textContent = "0 contextos activos";
    $("activeContextsPill").classList.remove("good");
    $("activeContextsPill").classList.add("muted");
    renderTree();
  }

  async function deleteProject(){
    if(!state.selectedProjectId){ toast("Selecciona un proyecto"); return; }
    const ok = confirm("¿Seguro que quieres eliminar el proyecto? Se borrarán sus chats y mensajes.");
    if(!ok) return;
    setStatus("Eliminando…");
    try{
      await api(`/api/projects/${state.selectedProjectId}`, { method:"DELETE" });

      // limpiar estado asociado
      state.expandedProjects.delete(state.selectedProjectId);
      delete state.chatsByProject[String(state.selectedProjectId)];

      state.selectedProjectId = null;
      state.selectedChatId = null;

      await refreshAll();
      goHome();
      toast("Proyecto eliminado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function createChat(){
    if(!state.selectedProjectId){ toast("Selecciona un proyecto"); return; }
    const title = prompt("Título del chat:", "Chat nuevo");
    if(title === null) return;
    const clean = title.trim();
    if(!clean){ toast("Título vacío"); return; }

    setStatus("Creando chat…");
    try{
      const r = await api(`/api/projects/${state.selectedProjectId}/chats`, {
        method:"POST",
        body: JSON.stringify({title: clean})
      });

      await refreshProjectChats(state.selectedProjectId);

      // Asegurar expandido y abrir chat recién creado
      state.expandedProjects.add(state.selectedProjectId);
      renderTree();
      await selectChat(r.id);

      toast("Chat creado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function deleteChat(chatId){
    const ok = confirm("¿Eliminar este chat? Se borrarán sus mensajes.");
    if(!ok) return;
    setStatus("Eliminando chat…");
    try{
      await api(`/api/chats/${chatId}`, { method:"DELETE" });

      if(state.selectedChatId === chatId){
        state.selectedChatId = null;
        state.messages = [];
        renderMessages();
        $("chatTitle").textContent = "Selecciona un chat";
      }

      await refreshProjectChats(state.selectedProjectId);
      renderTree();
      toast("Chat eliminado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function selectChat(id){
    state.selectedChatId = id;
    renderTree();

    setStatus("Cargando chat…");
    try{
      const chat = await api(`/api/chats/${id}`);
      $("chatTitle").textContent = "Chat: " + chat.title;
      state.messages = await api(`/api/chats/${id}/messages`);
      renderMessages();
      $("msgInput").focus();
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  // ---------- AGENT STREAMING ----------
  function addBubble(role, text, cls=""){
    const box = $("chatBox");
    const div = document.createElement("div");
    div.className = "bubble " + (role === "user" ? "user" : "assistant") + (cls ? " " + cls : "");
    div.textContent = text;
    box.appendChild(div);
    scrollChatToBottom();
    return div;
  }

  function addStepBubble(stepNum, command){
    const box = $("chatBox");
    const div = document.createElement("div");
    div.className = "bubble event";
    div.dataset.step = String(stepNum);
    div.dataset.done = "0";

    const cmdEsc = esc(command || "");
    div.innerHTML = `
      <div style="font-weight:800;">[PASO ${stepNum}] Ejecutando comando</div>
      <div class="cmdblock">
        <div class="lang">bash</div>
        <pre>${cmdEsc}</pre>
      </div>
      <div class="cmdblock out" style="margin-top:10px;">
        <div class="lang">output</div>
        <pre>[pendiente...]</pre>
      </div>
    `;
    box.appendChild(div);
    scrollChatToBottom();
    return div;
  }

  function completeStepBubble(div, ok, output){
    if(!div) return;
    div.dataset.done = "1";
    div.classList.remove("good");
    div.classList.remove("bad");
    div.classList.add(ok ? "good" : "bad");

    const status = ok ? "OK" : "ERROR";
    const out = esc(output || "(sin output)");

    const outPre = div.querySelector(".cmdblock.out pre");
    if(outPre){
      outPre.textContent = `[${status}]\n${output || "(sin output)"}`;
    }
    scrollChatToBottom();
  }

  async function sendMessage(){
    if(!state.selectedChatId){ toast("Selecciona un chat"); return; }
    const text = $("msgInput").value.trim();
    if(!text){ toast("Escribe un mensaje"); return; }

    disableSend(true);
    setStatus("Agente trabajando…");

    try{
      $("msgInput").value = "";
      addBubble("user", text);

      // Bubble del asistente en vivo (solo texto normal)
      const liveAssistant = addBubble("assistant", "");

      // Estado por streaming de pasos
      let stepCounter = 0;
      const stepsByCommand = new Map(); // command -> div
      let lastStepDiv = null;

      const res = await fetch(`/api/chats/${state.selectedChatId}/agent-stream`, {
        method:"POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({content: text})
      });

      if(!res.ok){
        const t = await res.text();
        throw new Error(t);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      function handleSSEBlock(block){
        const lines = block.split("\n").filter(Boolean);
        let ev = "message";
        let dataLine = null;
        for(const ln of lines){
          if(ln.startsWith("event:")) ev = ln.slice(6).trim();
          if(ln.startsWith("data:")) dataLine = ln.slice(5).trim();
        }
        if(!dataLine) return;

        let payload = {};
        try{ payload = JSON.parse(dataLine); }catch(e){ payload = {text: dataLine}; }

        if(ev === "assistant_chunk"){
          liveAssistant.textContent += payload.text || "";
          scrollChatToBottom();
          return;
        }

        if(ev === "tool_call"){
          const cmd = payload.command || "";
          stepCounter += 1;
          const div = addStepBubble(stepCounter, cmd);
          stepsByCommand.set(cmd, div);
          lastStepDiv = div;
          return;
        }

        if(ev === "tool_output"){
          const cmd = payload.command || "";
          const out = payload?.result?.output ?? "";
          const ok = !!payload?.result?.ok;

          const div = stepsByCommand.get(cmd) || lastStepDiv;
          completeStepBubble(div, ok, out);
          return;
        }

        if(ev === "error"){
          stepCounter += 1;
          const div = addStepBubble(stepCounter, "(error del agente)");
          completeStepBubble(div, false, payload.text || "error");
          return;
        }
      }

      while(true){
        const { value, done } = await reader.read();
        if(done) break;
        buffer += decoder.decode(value, {stream:true});

        let idx;
        while((idx = buffer.indexOf("\n\n")) >= 0){
          const block = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          if(block.trim().length) handleSSEBlock(block);
        }
      }

      // refrescar mensajes guardados en DB para mantener consistencia al recargar
      state.messages = await api(`/api/chats/${state.selectedChatId}/messages`);
      toast("Listo");
    }catch(e){
      toast("Error: " + e.message);
      const div = document.createElement("div");
      div.className = "bubble event bad";
      div.textContent = `[ERROR]\n${e.message || String(e)}`;
      $("chatBox").appendChild(div);
      scrollChatToBottom();
    }finally{
      disableSend(false);
      setStatus("Listo");
      $("msgInput").focus();
    }
  }

  // ---------- Context modal ----------
  function modalBackdropClick(e){
    if(e.target.id === "ctxModalBackdrop") closeContextsModal();
  }

  async function openContextsModal(){
    if(!state.selectedProjectId){ toast("Selecciona un proyecto"); return; }
    $("ctxModalBackdrop").style.display = "flex";
    await reloadAllContexts();
    await reloadProjectContexts();
    await reloadGroups();
    $("ctxModalProjectChip").textContent = "Proyecto: #" + state.selectedProjectId;
  }

  function closeContextsModal(){
    $("ctxModalBackdrop").style.display = "none";
    state.selectedGroupId = null;
    $("selectedGroupLabel").textContent = "(ninguno)";
    $("groupContextsSelect").value = "";
  }

  function fillExampleContext(){
    $("ctxName").value = "Entorno de ejecución";
    $("ctxContent").value =
`IMPORTANTE: Este proyecto permite ejecutar comandos de consola.
- Tipo de consola: Linux (bash) / Windows (PowerShell o CMD) -> especifica cuál.
- Directorio base de trabajo, si aplica.
- Restricciones, si las hay (opcional).
- Objetivo: el agente debe planear y ejecutar por pasos, mostrando comando y output.`;
  }

  async function reloadAllContexts(){
    state.allContexts = await api("/api/contexts");
    renderGroupSelectOptions();
  }

  async function reloadProjectContexts(){
    state.projectContexts = await api(`/api/projects/${state.selectedProjectId}/contexts`);
    renderProjectContextsModal();
    renderContextsPreview();
  }

  async function createGlobalContext(){
    const name = $("ctxName").value.trim();
    const content = $("ctxContent").value.trim();
    if(!name || !content){ toast("Completa nombre y contenido"); return; }
    setStatus("Guardando…");
    try{
      await api("/api/contexts", { method:"POST", body: JSON.stringify({name, content}) });
      $("ctxName").value = "";
      $("ctxContent").value = "";
      await reloadAllContexts();
      await reloadProjectContexts();
      toast("Contexto creado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function deleteGlobalContext(contextId){
    const ok = confirm("¿Borrar este contexto global? Se quitará de todos los proyectos y grupos.");
    if(!ok) return;
    setStatus("Borrando…");
    try{
      await api(`/api/contexts/${contextId}`, { method:"DELETE" });
      await reloadAllContexts();
      await reloadProjectContexts();
      await reloadGroups();
      toast("Contexto borrado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function toggleProjectContext(contextId, isActive){
    setStatus("Actualizando…");
    try{
      await api(`/api/projects/${state.selectedProjectId}/contexts/toggle`, {
        method:"POST",
        body: JSON.stringify({ context_id: contextId, is_active: isActive })
      });
      await reloadProjectContexts();
      toast(isActive ? "Activado" : "Desactivado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function reloadGroups(){
    state.groups = await api("/api/context-groups");
    renderGroups();
  }

  async function createGroup(){
    const name = $("groupName").value.trim();
    if(!name){ toast("Escribe un nombre de grupo"); return; }
    setStatus("Creando grupo…");
    try{
      const r = await api("/api/context-groups", { method:"POST", body: JSON.stringify({name}) });
      $("groupName").value = "";
      await reloadGroups();
      await selectGroup(r.id);
      toast("Grupo creado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function deleteGroup(groupId){
    const ok = confirm("¿Borrar este grupo? (No borra los contextos globales).");
    if(!ok) return;
    setStatus("Borrando grupo…");
    try{
      await api(`/api/context-groups/${groupId}`, { method:"DELETE" });
      if(state.selectedGroupId === groupId){
        state.selectedGroupId = null;
        $("selectedGroupLabel").textContent = "(ninguno)";
      }
      await reloadGroups();
      toast("Grupo borrado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function selectGroup(groupId){
    state.selectedGroupId = groupId;
    renderGroups();
    setStatus("Cargando grupo…");
    try{
      const items = await api(`/api/context-groups/${groupId}/items`);
      $("selectedGroupLabel").textContent = "#" + groupId;

      const selected = new Set((items.context_ids || []).map(String));
      const sel = $("groupContextsSelect");
      for(const opt of sel.options){
        opt.selected = selected.has(opt.value);
      }

      toast("Grupo listo");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function saveGroupItems(){
    if(!state.selectedGroupId){ toast("Selecciona un grupo"); return; }
    const sel = $("groupContextsSelect");
    const ids = Array.from(sel.selectedOptions).map(o => Number(o.value));
    setStatus("Guardando…");
    try{
      await api(`/api/context-groups/${state.selectedGroupId}/items`, {
        method:"POST",
        body: JSON.stringify({ context_ids: ids })
      });
      toast("Grupo actualizado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function activateSelectedGroup(isActive){
    if(!state.selectedGroupId){ toast("Selecciona un grupo"); return; }
    setStatus(isActive ? "Activando grupo…" : "Desactivando grupo…");
    try{
      await api(`/api/projects/${state.selectedProjectId}/contexts/apply-group`, {
        method:"POST",
        body: JSON.stringify({ group_id: state.selectedGroupId, is_active: isActive })
      });
      await reloadProjectContexts();
      toast(isActive ? "Grupo activado" : "Grupo desactivado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  // Keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    if(e.ctrlKey && e.key === "Enter"){
      e.preventDefault();
      sendMessage();
    }
    if(e.ctrlKey && (e.key === "k" || e.key === "K")){
      e.preventDefault();
      if(state.selectedProjectId) createChat();
      else toast("Selecciona un proyecto primero");
    }
    if(e.key === "Escape"){
      if($("ctxModalBackdrop").style.display === "flex") closeContextsModal();
    }
  });

  refreshAll();
</script>
</body>
</html>
"""
