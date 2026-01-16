from app.api.chats_api import router as chats_router
from app.api.contexts_api import router as contexts_router
from app.api.projects_api import router as projects_router
from app.ui import PAGE_HTML
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="MiniGPT Projects")

app.include_router(projects_router)
app.include_router(chats_router)
app.include_router(contexts_router)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE_HTML


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8011, reload=True)
