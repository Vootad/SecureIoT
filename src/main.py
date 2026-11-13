from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse

from pathlib import Path
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers.auth import router as auth_router
from routers.lock import router as lock_router
from routers.admin_users import router as admin_users_router
from routers.admin_locks import router as admin_locks_router
from routers.admin_permissions import router as admin_permissions_router
from routers.admin_audit import router as admin_audit_router
from routers.user_locks import router as user_locks_router


# SQLAlchemy convert python models to db tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(lock_router)
app.include_router(admin_users_router)
app.include_router(admin_locks_router)
app.include_router(admin_permissions_router)
app.include_router(admin_audit_router)
app.include_router(user_locks_router)


# Define the frontend directory.
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

# Serve frontend CSS and JavaScript files.
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# Serve the login page at the root URL.
@app.get("/")
def serve_login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


# Serve individual frontend pages.
@app.get("/login")
def serve_login():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/admin")
def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


@app.get("/user")
def serve_user():
    return FileResponse(FRONTEND_DIR / "user.html")


# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.get("/health")
def health():
    return {"status": "ok"}
