JS_MESSAGES = r"""
  // ---------------- MENSAJES + STREAMING AGENTE ----------------
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

      const liveAssistant = addBubble("assistant", "");

      let stepCounter = 0;
      const stepsByCommand = new Map();
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
"""
