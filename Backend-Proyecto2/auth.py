from fastapi import APIRouter, Request, Response, HTTPException, Cookie
from pydantic import BaseModel
from redis import Redis
from utils import hash_password, verify_password, create_access_token
import os
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

router = APIRouter()
# Conexión a Redis
redis_client = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)

class RegisterForm(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: RegisterForm):
    user_key = f"user:{user.username}"
    # Verifica si el usuario ya existe en Redis
    if redis_client.exists(user_key):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    # Guarda la información del usuario en un hash de Redis
    redis_client.hset(user_key, mapping={"username": user.username, "password": hashed})
    return {"message": "User registered"}

@router.post("/login")
def login(response: Response, user: RegisterForm):
    user_key = f"user:{user.username}"
    # Recupera los datos del usuario desde Redis
    user_data = redis_client.hgetall(user_key)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(user.password, user_data.get("password", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # Crea el token JWT
    token = create_access_token({"sub": user.username})
    # Guarda el token en Redis con un tiempo de expiración (30 días)
    redis_client.set(f"session:{user.username}", token, ex=60*60*24*30)
    # Establece la cookie de sesión en la respuesta
    response.set_cookie("session_token", token, httponly=True, max_age=60*60*24*30)
    return {"message": "Login successful"}

@router.get("/me")
def get_me(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Decodifica el token para obtener el username
        payload = jwt.decode(session_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verifica que el token almacenado en Redis coincida con el de la cookie
    stored_token = redis_client.get(f"session:{username}")
    if stored_token != session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"username": username}

@router.post("/logout")
def logout(response: Response, session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(session_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Borra el token de sesión de Redis
    redis_client.delete(f"session:{username}")
    # Elimina la cookie del cliente
    response.delete_cookie("session_token")
    return {"message": "Logged out"}