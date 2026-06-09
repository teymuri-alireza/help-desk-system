from fastapi import FastAPI
from fastapi_swagger import patch_fastapi
from src.server.routes.auth import router as auth_router
from src.server.routes.tickets import router as tickets_router
from src.server.routes.responses import router as responses_router
from src.server.routes.dashboard import router as dashboard_router
from src.server.routes.users import router as users_router
from src.server.routes.notifications import router as notifications_router

# Patch FastAPI to serve Swagger UI locally
app = FastAPI(docs_url=None, swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app=app, redirect_from_root_to_docs=False)

# Home Page
@app.get("/")
def root():
    return {"response": "Home Page"}

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(responses_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(notifications_router)
