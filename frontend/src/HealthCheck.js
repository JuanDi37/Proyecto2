// HealthCheck.js
import React, { useEffect, useState } from 'react';

const HealthCheck = () => {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => setHealth(data))
      .catch(error => console.error("Error en HealthCheck:", error));
  }, []);

  if (!health) return <div>Cargando Health Check...</div>;

  return (
    <div>
      <h3>Health Check</h3>
      <pre>{JSON.stringify(health, null, 2)}</pre>
    </div>
  );
};

export default HealthCheck;
