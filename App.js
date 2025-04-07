import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [username, setUsername] = useState(null);
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const [isRegistering, setIsRegistering] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/me", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => {
        if (response.ok) return response.json();
        throw new Error("No autenticado");
      })
      .then((data) => setUsername(data.username))
      .catch(() => setUsername(null));
  }, []);

  const handleInputChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const endpoint = isRegistering ? "register" : "login";
    fetch(`http://localhost:8000/${endpoint}`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Error en la petición");
        return response.json();
      })
      .then(() => {
        return fetch("http://localhost:8000/me", { credentials: "include" });
      })
      .then((response) => {
        if (response.ok) return response.json();
        throw new Error("Error al obtener la sesión");
      })
      .then((data) => {
        setUsername(data.username);
        setError(null);
      })
      .catch((err) => setError(err.message));
  };

  const handleLogout = () => {
    fetch("http://localhost:8000/logout", {
      method: "POST",
      credentials: "include",
    }).then((response) => {
      if (response.ok) {
        setUsername(null);
      }
    });
  };

  if (username) {
    return (
      <div className="container">
        <div className="welcome-card">
          <h1>Bienvenido, {username}</h1>
          <button className="logout-btn" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="auth-card">
        <h1>{isRegistering ? "Registro" : "Login"}</h1>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            className="input-field"
            type="text"
            name="username"
            placeholder="Usuario"
            value={form.username}
            onChange={handleInputChange}
            required
          />
          <input
            className="input-field"
            type="password"
            name="password"
            placeholder="Contraseña"
            value={form.password}
            onChange={handleInputChange}
            required
          />
          <button className="submit-btn" type="submit">
            {isRegistering ? "Registrar" : "Iniciar sesión"}
          </button>
        </form>
        <button
          className="toggle-btn"
          onClick={() => setIsRegistering(!isRegistering)}
        >
          {isRegistering
            ? "¿Ya tienes cuenta? Inicia sesión"
            : "¿No tienes cuenta? Regístrate"}
        </button>
      </div>
    </div>
  );
}

export default App;