// C:\Users\Juan Diego\Downloads\frontend\src\Login.js
import React, { useState } from 'react';
import Cookies from 'js-cookie';

function Login({ setLoggedIn }) {
    // Usuario por defecto: admin / 123
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('123');

    const handleLogin = async () => {
        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        if (response.ok) {
            Cookies.set('loggedIn', 'true', { expires: 30 });
            setLoggedIn(true);
        } else {
            alert("Login failed");
        }
    };

    return (
        <div>
            <h2>Login</h2>
            <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
            <button onClick={handleLogin}>Login</button>
        </div>
    );
}

export default Login;
