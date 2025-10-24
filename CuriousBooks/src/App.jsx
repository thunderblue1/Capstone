import React, { useState, useEffect } from 'react';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('/api/data') // This will be proxied to http://localhost:5000/api/data
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div>
      <h1>React Frontend</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;
