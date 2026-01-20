JS_CONTEXTS = r"""
  // ---------------- CONTEXTOS (MODAL) + GRUPOS ----------------
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
"""
