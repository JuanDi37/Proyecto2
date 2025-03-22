# C:\Users\Juan Diego\Downloads\backend\schemas.py
from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str  # Antes decía email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# Product schema
class ProductBase(BaseModel):
    name: str
    price: float
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductCategoryBase(BaseModel):
    name: str

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryResponse(ProductCategoryBase):
    id: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Cart(BaseModel):
    items: List[CartItem] = []
