from app.ui_parts.layout import PAGE_SHELL_HTML
from app.ui_parts.styles import STYLE_CSS
from app.ui_parts.scripts import APP_JS


PAGE_HTML = PAGE_SHELL_HTML.format(
    STYLE_CSS=STYLE_CSS,
    APP_JS=APP_JS,
)