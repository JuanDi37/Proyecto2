// C:\Users\Juan Diego\Downloads\frontend\src\App.js
import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import Login from './Login';

function App() {
  const [loggedIn, setLoggedIn] = useState(Cookies.get('loggedIn') === 'true');
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');

  // Recuperar el carrito de las cookies (persistencia de 30 días)
  const getStoredCart = () => {
    const cookieCart = Cookies.get('cart');
    return cookieCart ? JSON.parse(cookieCart) : [];
  };

  const [cart, setCart] = useState(getStoredCart());

  // Recuperar compras previas desde cookies
  const getStoredPrevPurchases = () => {
    const cookiePrev = Cookies.get('comprasPrevias');
    return cookiePrev ? JSON.parse(cookiePrev) : [];
  };

  const [prevPurchases, setPrevPurchases] = useState(getStoredPrevPurchases());

  useEffect(() => {
    fetch("http://localhost:8000/products")
      .then(response => response.json())
      .then(data => setProducts(data));
    fetch("http://localhost:8000/categories")
      .then(response => response.json())
      .then(data => setCategories(data));
  }, []);

  // Actualiza la cookie del carrito cada vez que cambie
  useEffect(() => {
    Cookies.set('cart', JSON.stringify(cart), { expires: 30 });
  }, [cart]);

  // Actualiza la cookie de compras previas cada vez que cambie
  useEffect(() => {
    Cookies.set('comprasPrevias', JSON.stringify(prevPurchases), { expires: 30 });
  }, [prevPurchases]);

  const addToCart = (product) => {
    setCart(prevCart => {
      const existing = prevCart.find(item => item.id === product.id);
      if (existing) {
        return prevCart.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      } else {
        return [...prevCart, { ...product, quantity: 1 }];
      }
    });
  };

  const checkout = () => {
    const payload = { items: cart.map(item => ({ product_id: item.id, quantity: item.quantity })) };
    fetch("http://localhost:8000/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(async (response) => {
      if(response.ok) {
        alert("Checkout successful!");
        // Guardar la compra actual en compras previas
        setPrevPurchases(prev => [...prev, cart]);
        // Limpiar el carrito y eliminar la cookie
        setCart([]);
        Cookies.remove('cart');
      } else {
        const errorMsg = await response.text();
        alert(`Checkout failed: ${errorMsg}`);
      }
    })
    .catch(error => {
      console.error("Error during checkout:", error);
      alert("Checkout error!");
    });
  };

  return (
    <div>
      <h1>Online Store</h1>
      {!loggedIn ? (
        <Login setLoggedIn={setLoggedIn} />
      ) : (
        <>
          <select onChange={(e) => setSelectedCategory(e.target.value)}>
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </select>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {products
              .filter(product => !selectedCategory || product.category_id === selectedCategory)
              .map(product => (
                <li key={product.id} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <img
                        src={product.image_url}
                        alt={product.name}
                        style={{ width: '100px', height: '100px', marginRight: '10px', borderRadius: '5px' }}
                      />
                      <div>
                        <h3>{product.name}</h3>
                        <p>${product.price.toFixed(2)}</p>
                        <p>Stock: {product.stock}</p>
                      </div>
                    </div>
                    <button onClick={() => addToCart(product)}>Agregar al Carrito</button>
                  </div>
                </li>
              ))}
          </ul>
          {cart.length > 0 && (
            <div style={{ border: '1px solid #000', padding: '10px', marginTop: '20px' }}>
              <h2>Carrito</h2>
              <ul>
                {cart.map(item => (
                  <li key={item.id}>
                    {item.name} - Cantidad: {item.quantity}
                  </li>
                ))}
              </ul>
              <button onClick={checkout}>Pay</button>
            </div>
          )}
          {prevPurchases.length > 0 && (
            <div style={{ border: '1px solid #666', padding: '10px', marginTop: '20px' }}>
              <h2>Compras Previas</h2>
              {prevPurchases.map((purchase, index) => (
                <div key={index} style={{ marginBottom: '10px' }}>
                  <h3>Compra {index + 1}</h3>
                  <ul>
                    {purchase.map(item => (
                      <li key={item.id}>
                        {item.name} - Cantidad: {item.quantity}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
