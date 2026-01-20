from app.ui_parts.js_core import JS_CORE
from app.ui_parts.js_tree import JS_TREE
from app.ui_parts.js_messages import JS_MESSAGES
from app.ui_parts.js_contexts import JS_CONTEXTS
from app.ui_parts.js_shortcuts import JS_SHORTCUTS


APP_JS = "\n".join([
    JS_CORE,
    JS_TREE,
    JS_MESSAGES,
    JS_CONTEXTS,
    JS_SHORTCUTS,
])
