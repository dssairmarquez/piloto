JS_CORE = r"""
  // ---------------- CORE / STATE / HELPERS ----------------
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

  async function refreshAll(){
    setStatus("Cargando…");
    try{
      state.projects = await api("/api/projects");
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
"""
