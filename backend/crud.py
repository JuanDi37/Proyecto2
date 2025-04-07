# backend/crud.py
from fastapi import HTTPException, status
import schemas

# Funciones para User
def create_user(r, user: schemas.UserCreate):
    # Verificar que el nombre de usuario no exista (guardamos un mapping username -> id)
    if r.exists(f"username:{user.username}"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")
    user_id = r.incr("user:id")
    key = f"user:{user_id}"
    r.hset(key, mapping={"id": user_id, "username": user.username, "password": user.password})
    r.set(f"username:{user.username}", user_id)
    return {"id": user_id, "username": user.username}

def authenticate_user(r, user: schemas.UserLogin):
    user_id = r.get(f"username:{user.username}")
    if not user_id:
        return None
    key = f"user:{user_id}"
    stored_password = r.hget(key, "password")
    if stored_password == user.password:
        return {"id": int(user_id), "username": user.username}
    return None

def get_user(r, user_id: int):
    key = f"user:{user_id}"
    user_data = r.hgetall(key)
    if not user_data:
        return None
    user_data["id"] = int(user_data["id"])
    return user_data

# Funciones para Product
def create_product(r, product: schemas.ProductCreate):
    product_id = r.incr("product:id")
    key = f"product:{product_id}"
    data = product.dict()
    data["id"] = product_id
    # Asignar stock por defecto (similar al campo "stock" en tu modelo original)
    data.setdefault("stock", 10)
    r.hset(key, mapping=data)
    r.sadd("products", product_id)
    return data

def get_products(r):
    product_ids = r.smembers("products")
    products = []
    for pid in product_ids:
        key = f"product:{pid}"
        product = r.hgetall(key)
        if product:
            product["id"] = int(product["id"])
            product["price"] = float(product["price"])
            product["stock"] = int(product["stock"])
            product["category_id"] = int(product["category_id"])
            products.append(product)
    return products

# Funciones para Category
def create_category(r, category: schemas.ProductCategoryCreate):
    if r.exists(f"category:name:{category.name}"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists.")
    category_id = r.incr("category:id")
    key = f"category:{category_id}"
    data = {"id": category_id, "name": category.name}
    r.hset(key, mapping=data)
    r.set(f"category:name:{category.name}", category_id)
    r.sadd("categories", category_id)
    return data

def get_categories(r):
    category_ids = r.smembers("categories")
    categories = []
    for cid in category_ids:
        key = f"category:{cid}"
        cat = r.hgetall(key)
        if cat:
            cat["id"] = int(cat["id"])
            categories.append(cat)
    return categories

# Funciones para Order
def create_order(r, cart: schemas.Cart, user_id: int = 1):
    order_id = r.incr("order:id")
    order_key = f"order:{order_id}"
    r.hset(order_key, mapping={"id": order_id, "user_id": user_id})
    order_items_key = f"order:{order_id}:items"
    pipe = r.pipeline()
    for item in cart.items:
        product_key = f"product:{item.product_id}"
        product = r.hgetall(product_key)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id {item.product_id} no encontrado."
            )
        if int(product.get("stock", 0)) < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para el producto {product.get('name')}. Disponible: {product.get('stock')}"
            )
        # Reducir el stock
        pipe.hincrby(product_key, "stock", -item.quantity)
        # Guardar el item de la orden en una lista con el formato "product_id:quantity"
        pipe.rpush(order_items_key, f"{item.product_id}:{item.quantity}")
    pipe.execute()
    return {"order_id": order_id, "message": "Order created successfully"}
