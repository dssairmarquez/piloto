STYLE_CSS = r"""
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
"""
