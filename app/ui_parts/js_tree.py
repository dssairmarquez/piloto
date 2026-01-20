JS_TREE = r"""
  // ---------------- PROYECTOS / CHATS TREE ----------------
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

    if(state.selectedProjectId !== projectId){
      await selectProject(projectId, { autoExpand: true });
      return;
    }

    if(wasOpen) state.expandedProjects.delete(projectId);
    else state.expandedProjects.add(projectId);

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

      await ensureChatsLoaded(id);

      state.projectContexts = await api(`/api/projects/${id}/contexts`);
      renderContextsPreview();

      renderTree();
      toast("Proyecto cargado");
    }catch(e){
      toast("Error: " + e.message);
    }finally{
      setStatus("Listo");
    }
  }

  async function deleteProject(){
    if(!state.selectedProjectId){ toast("Selecciona un proyecto"); return; }
    const ok = confirm("¿Seguro que quieres eliminar el proyecto? Se borrarán sus chats y mensajes.");
    if(!ok) return;
    setStatus("Eliminando…");
    try{
      await api(`/api/projects/${state.selectedProjectId}`, { method:"DELETE" });

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
"""
