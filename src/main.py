from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest):
    return {
        "username": request.username,
        "message": "Login request received"
    }


@app.post("/lock/unlock")
def unlock():
    return {"message": "Unlock endpoint"}
