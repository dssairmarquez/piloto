PAGE_HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>MiniGPT Projects</title>
  <style>
    :root{
      --bg:#0b0f17; --card:#111827; --muted:#94a3b8; --text:#e5e7eb;
      --line:#1f2937; --accent:#60a5fa; --good:#34d399; --bad:#fb7185;
      --shadow: 0 10px 30px rgba(0,0,0,.35);
      --r:16px;
    }
    *{box-sizing:border-box}
    body{
      margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans";
      background: radial-gradient(1200px 600px at 20% -20%, rgba(96,165,250,.25), transparent),
                  radial-gradient(900px 500px at 90% 0%, rgba(52,211,153,.16), transparent),
                  var(--bg);
      color:var(--text);
    }
    .wrap{max-width:1200px; margin:0 auto; padding:18px}
    header{
      display:flex; align-items:center; gap:12px; justify-content:space-between;
      padding:12px 14px; border:1px solid var(--line); border-radius:var(--r);
      background: rgba(17,24,39,.85); box-shadow: var(--shadow);
      position: sticky; top: 10px; backdrop-filter: blur(10px); z-index: 10;
    }
    header h1{font-size:16px; margin:0; letter-spacing:.3px}
    header .pill{font-size:12px; color:var(--muted)}
    .grid{display:grid; gap:14px; margin-top:14px}
    @media(min-width:980px){ .grid{grid-template-columns: 320px 1fr} }

    .card{
      border:1px solid var(--line); border-radius:var(--r); background: rgba(17,24,39,.85);
      box-shadow: var(--shadow); overflow:hidden;
    }
    .card .hd{
      padding:12px 14px; border-bottom:1px solid var(--line);
      display:flex; align-items:center; justify-content:space-between; gap:10px;
    }
    .card .hd h2{margin:0; font-size:13px; color:var(--muted); font-weight:600; text-transform: uppercase; letter-spacing:.9px}
    .card .bd{padding:12px 14px}
    .row{display:flex; gap:10px; align-items:center}
    .col{display:flex; flex-direction:column; gap:10px}
    input, textarea, select{
      width:100%; padding:10px 10px; border-radius:12px; border:1px solid var(--line);
      background:#0b1220; color:var(--text); outline:none;
    }
    textarea{min-height:96px; resize:vertical}
    button{
      padding:10px 12px; border-radius:12px; border:1px solid var(--line);
      background: linear-gradient(180deg, rgba(96,165,250,.22), rgba(96,165,250,.12));
      color:var(--text); cursor:pointer; transition: transform .08s ease, border-color .15s ease, opacity .15s ease;
      user-select:none;
    }
    button:hover{transform: translateY(-1px); border-color: rgba(96,165,250,.5)}
    button:disabled{opacity:.5; cursor:not-allowed; transform:none}
    .btn-ghost{ background: transparent; }
    .btn-good{
      background: linear-gradient(180deg, rgba(52,211,153,.22), rgba(52,211,153,.12));
    }
    .btn-bad{
      background: linear-gradient(180deg, rgba(251,113,133,.22), rgba(251,113,133,.12));
    }
    .list{
      display:flex; flex-direction:column; gap:8px;
      max-height: 440px; overflow:auto; padding-right:4px;
    }
    .item{
      border:1px solid var(--line); border-radius:14px; padding:10px 10px; background: rgba(11,18,32,.75);
      display:flex; flex-direction:column; gap:8px;
    }
    .item .top{display:flex; align-items:center; justify-content:space-between; gap:10px}
    .item .title{font-weight:650; font-size:13px}
    .item .meta{font-size:12px; color:var(--muted)}
    .tag{
      font-size:11px; color:#0b0f17; background: rgba(52,211,153,.95);
      padding:4px 8px; border-radius:999px; font-weight:700; letter-spacing:.2px;
    }
    .tag.inactive{background: rgba(148,163,184,.9)}
    .split{display:grid; gap:12px}
    @media(min-width:900px){ .split{grid-template-columns: 1fr 1fr} }

    .chatbox{
      height: 520px; overflow:auto; border:1px solid var(--line); border-radius: 16px;
      padding: 12px; background: rgba(11,18,32,.65);
      display:flex; flex-direction:column; gap:10px;
    }
    .bubble{
      max-width: 86%; padding:10px 12px; border-radius: 16px;
      border:1px solid var(--line);
      white-space: pre-wrap; line-height:1.35; font-size:14px;
    }
    .bubble.user{align-self:flex-end; background: rgba(96,165,250,.12); border-color: rgba(96,165,250,.28)}
    .bubble.assistant{align-self:flex-start; background: rgba(148,163,184,.10)}
    .toast{
      position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
      background: rgba(17,24,39,.92); border:1px solid var(--line); color:var(--text);
      padding:10px 12px; border-radius: 999px; box-shadow: var(--shadow);
      font-size: 13px; opacity:0; pointer-events:none; transition: opacity .15s ease;
      max-width: 92vw;
      z-index: 50;
    }
    .toast.show{opacity:1}
    .hint{font-size:12px; color:var(--muted); margin-top:8px}
    .divider{height:1px; background: var(--line); margin: 12px 0}
    .kbd{font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
         font-size: 11px; padding: 2px 6px; border-radius: 8px; border:1px solid var(--line);
         background: rgba(11,18,32,.8); color: var(--muted)}

    /* Modal */
    .modal-backdrop{
      position: fixed; inset:0; background: rgba(0,0,0,.55);
      display:none; align-items:center; justify-content:center;
      z-index: 40;
      padding: 18px;
    }
    .modal{
      width: min(1100px, 98vw);
      max-height: 92vh;
      overflow:auto;
      border:1px solid var(--line);
      border-radius: 18px;
      background: rgba(17,24,39,.92);
      box-shadow: var(--shadow);
    }
    .modal .mhd{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      display:flex; align-items:center; justify-content:space-between; gap:12px;
      position: sticky; top: 0;
      background: rgba(17,24,39,.96);
      backdrop-filter: blur(10px);
    }
    .modal .mbd{ padding: 12px 14px; }
    .chip{
      border: 1px solid var(--line);
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      color: var(--muted);
      background: rgba(11,18,32,.55);
    }
    .toggle{
      display:flex; align-items:center; justify-content:space-between;
      border:1px solid var(--line); border-radius:14px; padding:10px;
      background: rgba(11,18,32,.70);
      gap:12px;
    }
    .toggle .left{display:flex; flex-direction:column; gap:4px}
    .toggle .right{display:flex; gap:8px; align-items:center}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="row" style="gap:10px;">
        <h1>MiniGPT Projects</h1>
        <span class="pill" id="statusPill">Listo</span>
      </div>
      <div class="row" style="gap:8px;">
        <span class="pill">Atajos: <span class="kbd">Ctrl</span>+<span class="kbd">K</span> nuevo chat · <span class="kbd">Ctrl</span>+<span class="kbd">Enter</span> enviar</span>
      </div>
    </header>

    <div class="grid">
      <!-- Left -->
      <div class="card">
        <div class="hd">
          <h2>Proyectos</h2>
          <button class="btn-ghost" onclick="refreshAll()">↻</button>
        </div>
        <div class="bd col">
          <div class="row">
            <input id="projectName" placeholder="Nombre del proyecto"/>
            <button onclick="createProject()">Crear</button>
          </div>
          <div class="list" id="projectsList"></div>
          <div class="hint">Primero crea/elige un proyecto. Dentro podrás crear chats y gestionar contextos globales.</div>
        </div>
      </div>

      <!-- Right -->
      <div class="card">
        <div class="hd">
          <h2 id="projectTitle">Selecciona un proyecto</h2>
          <div class="row">
            <button class="btn-ghost" onclick="goHome()">Inicio</button>
          </div>
        </div>
        <div class="bd">
          <div id="projectPanel" style="display:none;">
            <div class="split">
              <!-- Contexts summary -->
              <div class="col">
                <div class="row" style="justify-content:space-between;">
                  <div style="font-weight:700;">Contextos</div>
                  <span class="pill" id="activeContextsPill">0 activos</span>
                </div>

                <div class="item">
                  <div class="title">Gestión</div>
                  <div class="meta">Los contextos son globales y se activan/desactivan por proyecto.</div>
                  <div class="row">
                    <button class="btn-good" onclick="openContextsModal()">Gestionar contextos</button>
                    <button class="btn-bad" onclick="deleteProject()">Eliminar proyecto</button>
                  </div>
                  <div class="hint">Consejo: puedes activar varios contextos a la vez.</div>
                </div>

                <div class="list" id="contextsPreviewList"></div>
              </div>

              <!-- Chats -->
              <div class="col">
                <div class="row" style="justify-content:space-between;">
                  <div style="font-weight:700;">Chats</div>
                  <button class="btn-good" onclick="createChat()">+ Nuevo chat</button>
                </div>

                <div class="list" id="chatsList"></div>

                <div class="divider"></div>

                <div style="font-weight:700; margin-bottom:8px;" id="chatTitle">Selecciona un chat</div>
                <div class="chatbox" id="chatBox"></div>
                <div class="row" style="margin-top:10px;">
                  <textarea id="msgInput" placeholder="Escribe tu mensaje... (Ctrl+Enter para enviar)" style="min-height:52px;"></textarea>
                  <button id="sendBtn" onclick="sendMessage()" style="min-width:120px;">Enviar</button>
                </div>
                <div class="hint">
                  Si no hay API key, verás el error al enviar.
                </div>
              </div>
            </div>
          </div>

          <div id="emptyPanel" class="hint" style="display:block;">
            Elige un proyecto a la izquierda para ver sus contextos y chats.
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal -->
  <div class="modal-backdrop" id="ctxModalBackdrop" onclick="modalBackdropClick(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="mhd">
        <div class="row" style="gap:10px;">
          <div style="font-weight:800;">Contextos globales</div>
          <span class="chip" id="ctxModalProjectChip">Proyecto: -</span>
        </div>
        <div class="row">
          <button class="btn-ghost" onclick="closeContextsModal()">Cerrar</button>
        </div>
      </div>
      <div class="mbd">
        <div class="split">
          <!-- Left: contexts -->
          <div class="col">
            <div class="item">
              <div class="title">Crear contexto global</div>
              <input id="ctxName" placeholder="Nombre (ej: 'Soporte técnico')"/>
              <textarea id="ctxContent" placeholder="Contenido del contexto: reglas, tono, datos, etc."></textarea>
              <div class="row">
                <button class="btn-good" onclick="createGlobalContext()">Guardar</button>
                <button class="btn-ghost" onclick="fillExampleContext()">Ejemplo</button>
              </div>
            </div>

            <div class="row" style="justify-content:space-between;">
              <div style="font-weight:700;">Activar/desactivar en este proyecto</div>
              <button class="btn-ghost" onclick="reloadProjectContexts()">↻</button>
            </div>
            <div class="list" id="projectContextsList"></div>
          </div>

          <!-- Right: groups -->
          <div class="col">
            <div class="item">
              <div class="title">Crear grupo</div>
              <input id="groupName" placeholder="Nombre del grupo (ej: 'Ecommerce')"/>
              <div class="row">
                <button class="btn-good" onclick="createGroup()">Crear grupo</button>
              </div>
              <div class="hint">Los grupos organizan contextos existentes.</div>
            </div>

            <div class="row" style="justify-content:space-between;">
              <div style="font-weight:700;">Grupos</div>
              <button class="btn-ghost" onclick="reloadGroups()">↻</button>
            </div>
            <div class="list" id="groupsList"></div>

            <div class="item">
              <div class="title">Editar grupo: <span id="selectedGroupLabel" style="color:var(--muted)">(ninguno)</span></div>
              <div class="meta">Selecciona un grupo arriba para editar sus contextos.</div>
              <select id="groupContextsSelect" multiple size="10"></select>
              <div class="row">
                <button class="btn-good" onclick="saveGroupItems()">Guardar contexts del grupo</button>
                <button class="btn-ghost" onclick="activateSelectedGroup(true)">Activar grupo en proyecto</button>
                <button class="btn-ghost" onclick="activateSelectedGroup(false)">Desactivar grupo en proyecto</button>
              </div>
              <div class="hint">Tip: Ctrl/Cmd para seleccionar varios en el select.</div>
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
    chats: [],
    messages: [],
    projectContexts: [], // global contexts + active flag for project
    groups: [],
    allContexts: []
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

  // ---------- Render ----------
  function renderProjects(){
    const list = $("projectsList");
    list.innerHTML = "";
    for(const p of state.projects){
      const isSel = (p.id === state.selectedProjectId);
      const el = document.createElement("div");
      el.className = "item";
      el.style.borderColor = isSel ? "rgba(96,165,250,.55)" : "";
      el.innerHTML = `
        <div class="top">
          <div>
            <div class="title">${esc(p.name)}</div>
            <div class="meta">#${p.id} · ${esc(p.created_at)}</div>
          </div>
          <div class="row">
            <button class="btn-ghost" onclick="selectProject(${p.id})">${isSel ? "✓" : "Abrir"}</button>
          </div>
        </div>
      `;
      list.appendChild(el);
    }
    if(state.projects.length === 0){
      list.innerHTML = `<div class="hint">No hay proyectos. Crea el primero arriba.</div>`;
    }
  }

  function renderChats(){
    const list = $("chatsList");
    list.innerHTML = "";
    for(const ch of state.chats){
      const isSel = (ch.id === state.selectedChatId);
      const el = document.createElement("div");
      el.className = "item";
      el.style.borderColor = isSel ? "rgba(52,211,153,.55)" : "";
      el.innerHTML = `
        <div class="top">
          <div>
            <div class="title">${esc(ch.title)}</div>
            <div class="meta">#${ch.id} · ${esc(ch.created_at)}</div>
          </div>
          <div class="row">
            <button class="btn-ghost" onclick="selectChat(${ch.id})">${isSel ? "✓" : "Abrir"}</button>
            <button class="btn-bad" onclick="deleteChat(${ch.id})">Eliminar</button>
          </div>
        </div>
      `;
      list.appendChild(el);
    }
    if(state.chats.length === 0){
      list.innerHTML = `<div class="hint">No hay chats. Crea uno con “Nuevo chat”.</div>`;
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
    const list = $("contextsPreviewList");
    list.innerHTML = "";
    const active = state.projectContexts.filter(x => x.is_active === 1);
    $("activeContextsPill").textContent = `${active.length} activos`;
    $("activeContextsPill").style.color = active.length ? "var(--good)" : "var(--muted)";

    if(active.length === 0){
      list.innerHTML = `<div class="hint">No hay contextos activos. Abre el modal para activar alguno.</div>`;
      return;
    }

    for(const c of active){
      const el = document.createElement("div");
      el.className = "item";
      el.innerHTML = `
        <div class="top">
          <div>
            <div class="title">${esc(c.name)}</div>
            <div class="meta">${esc(c.created_at)}</div>
          </div>
          <span class="tag">ACTIVO</span>
        </div>
        <div class="meta" style="white-space:pre-wrap;">${esc(c.content)}</div>
      `;
      list.appendChild(el);
    }
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
          <div style="font-weight:750;">${esc(c.name)}</div>
          <div class="meta" style="white-space:pre-wrap;">${esc(c.content)}</div>
        </div>
        <div class="right">
          <span class="${isActive ? "tag" : "tag inactive"}">${isActive ? "ACTIVO" : "INACTIVO"}</span>
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
      el.className = "item";
      el.style.borderColor = isSel ? "rgba(96,165,250,.55)" : "";
      el.innerHTML = `
        <div class="top">
          <div>
            <div class="title">${esc(g.name)}</div>
            <div class="meta">#${g.id} · ${esc(g.created_at)}</div>
          </div>
          <div class="row">
            <button class="btn-ghost" onclick="selectGroup(${g.id})">${isSel ? "✓" : "Editar"}</button>
            <button class="btn-bad" onclick="deleteGroup(${g.id})">Borrar</button>
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

  function showProjectPanel(show){
    $("projectPanel").style.display = show ? "block" : "none";
    $("emptyPanel").style.display = show ? "none" : "block";
  }

  // ---------- Actions ----------
  async function refreshAll(){
    setStatus("Cargando…");
    try{
      state.projects = await api("/api/projects");
      renderProjects();
      if(state.selectedProjectId){
        await loadProject(state.selectedProjectId);
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

  async function selectProject(id){
    state.selectedProjectId = id;
    state.selectedChatId = null;
    renderProjects();
    await loadProject(id);
  }

  async function loadProject(id){
    setStatus("Cargando proyecto…");
    try{
      const project = await api(`/api/projects/${id}`);
      $("projectTitle").textContent = "Proyecto: " + project.name;
      showProjectPanel(true);

      state.chats = await api(`/api/projects/${id}/chats`);
      state.messages = [];
      renderChats();
      renderMessages();
      $("chatTitle").textContent = "Selecciona un chat";

      // contexts preview
      state.projectContexts = await api(`/api/projects/${id}/contexts`);
      renderContextsPreview();

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
    renderProjects();
  }

  async function deleteProject(){
    if(!state.selectedProjectId){ toast("Selecciona un proyecto"); return; }
    const ok = confirm("¿Seguro que quieres eliminar el proyecto? Se borrarán sus chats y mensajes.");
    if(!ok) return;
    setStatus("Eliminando…");
    try{
      await api(`/api/projects/${state.selectedProjectId}`, { method:"DELETE" });
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
      state.chats = await api(`/api/projects/${state.selectedProjectId}/chats`);
      renderChats();
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
      state.chats = await api(`/api/projects/${state.selectedProjectId}/chats`);
      renderChats();
      toast("Chat eliminado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function selectChat(id){
    state.selectedChatId = id;
    renderChats();
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

  async function sendMessage(){
    if(!state.selectedChatId){ toast("Selecciona un chat"); return; }
    const text = $("msgInput").value.trim();
    if(!text){ toast("Escribe un mensaje"); return; }

    disableSend(true);
    setStatus("Pensando…");
    try{
      $("msgInput").value = "";

      state.messages.push({role:"user", content:text});
      renderMessages();

      await api(`/api/chats/${state.selectedChatId}/messages`, {
        method:"POST",
        body: JSON.stringify({content:text})
      });

      state.messages = await api(`/api/chats/${state.selectedChatId}/messages`);
      renderMessages();
      toast("Respuesta lista");
    }catch(e){
      toast("Error: " + e.message);
      state.messages.push({role:"assistant", content:"Error: " + e.message});
      renderMessages();
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
    $("ctxName").value = "Asistente de producto";
    $("ctxContent").value =
`Eres un asistente especializado en ayudar a usuarios a usar este producto.
Reglas:
- Da pasos accionables y claros.
- Si hay ambigüedad, pregunta 1-2 cosas como máximo.
- Si el usuario pide código, entrega un ejemplo mínimo + mejores prácticas.
Tono: cercano, profesional y breve.`;
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

  // ---------- Groups ----------
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

      // set selected options
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
