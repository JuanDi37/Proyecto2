# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_client import redis_client
import schemas, crud

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_redis():
    return redis_client

@app.post("/register")
def register_user(user: schemas.UserCreate, r = Depends(get_redis)):
    return crud.create_user(r, user)

@app.post("/login")
def login_user(user: schemas.UserLogin, r = Depends(get_redis)):
    auth_user = crud.authenticate_user(r, user)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth_user

@app.get("/products")
def get_products(r = Depends(get_redis)):
    return crud.get_products(r)

@app.get("/categories")
def get_categories(r = Depends(get_redis)):
    return crud.get_categories(r)

@app.post("/checkout")
def checkout(cart: schemas.Cart, r = Depends(get_redis)):
    return crud.create_order(r, cart, user_id=1)

@app.get("/health")
def health_check(r = Depends(get_redis)):
    try:
        r.ping()
        return {"status": "ok", "result": "Redis is alive"}
    except Exception:
        raise HTTPException(status_code=500, detail="Redis error")
