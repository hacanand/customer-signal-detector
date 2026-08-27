from app.api.router import api_router
from app.core.factory import create_app

app = create_app()
app.include_router(api_router)
