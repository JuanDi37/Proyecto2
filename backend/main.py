# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # Importación añadida
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud.authenticate_user(db, user)

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@app.post("/checkout")
def checkout(cart: schemas.Cart, db: Session = Depends(get_db)):
    return crud.create_order(db, cart, user_id=1)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).fetchone()  # Uso de text() añadido
    return {"status": "ok", "result": result[0]}
