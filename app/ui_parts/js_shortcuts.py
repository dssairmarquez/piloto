JS_SHORTCUTS = r"""
  // ---------------- SHORTCUTS + INIT ----------------
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
"""
