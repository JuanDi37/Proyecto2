# C:\Users\Juan Diego\Downloads\backend\crud.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models, schemas

# CRUD functions for User
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, user: schemas.UserLogin):
    return db.query(models.User).filter(
        models.User.username == user.username, 
        models.User.password == user.password
    ).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# CRUD functions for Product
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session):
    return db.query(models.Product).all()

# CRUD functions for Category
def create_category(db: Session, category: schemas.ProductCategoryCreate):
    db_category = models.ProductCategory(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session):
    return db.query(models.ProductCategory).all()


def create_order(db: Session, cart: schemas.Cart, user_id: int = 1):
    # Crear la orden sin hacer commit inmediato (para hacer la operación atómica)
    order = models.Order(user_id=user_id)
    db.add(order)
    
    for item in cart.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {item.product_id} no encontrado."
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para el producto {product.name}. Disponible: {product.stock}"
            )
        # Reducir el stock
        product.stock -= item.quantity
        # Crear el item de la orden
        order_item = models.OrderItem(
            order_id=order.id, 
            product_id=item.product_id, 
            quantity=item.quantity
        )
        db.add(order_item)
    
    # Commit atómico de la orden y actualización de stock
    db.commit()
    db.refresh(order)
    return {"order_id": order.id, "message": "Order created successfully"}