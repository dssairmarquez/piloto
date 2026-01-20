PAGE_SHELL_HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>MiniGPT Projects</title>
  <style>
{STYLE_CSS}
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
{APP_JS}
  </script>
</body>
</html>
"""
