import React, { useState, useEffect } from 'react';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(`/user/${encodeURIComponent('John Keen')}`) // This will be proxied to http://localhost:5000/api/data
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        console.log(); 
        setMessage(data.message)
      }
      )
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div>
      <h1>React Frontend: {message}</h1>
    </div>
  );
}

export default App;
