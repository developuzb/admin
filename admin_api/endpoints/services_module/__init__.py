from .list import router as list_router
from .add import router as add_router
from .edit import router as edit_router
from .toggle import router as toggle_router

routers = [list_router, add_router, edit_router, toggle_router]
