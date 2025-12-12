import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import { logger } from './services/logger';

// Log application startup
logger.application.startup({
  appName: 'CuriousBooks',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  environment: import.meta.env.MODE,
});

// Log configuration loading
logger.config.loaded('vite-environment', {
  mode: import.meta.env.MODE,
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  logServerUrl: import.meta.env.VITE_LOG_SERVER_URL || 'http://localhost:5001',
});

const rootElement = document.getElementById('root');

if (!rootElement) {
  logger.error.critical('Root element not found', {
    component: 'main',
    errorCode: 'ROOT_ELEMENT_MISSING',
  });
  throw new Error('Root element not found');
}

const root = createRoot(rootElement);

root.render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);

// Log application ready after render
requestAnimationFrame(() => {
  logger.application.ready({
    appName: 'CuriousBooks',
    renderComplete: true,
  });
});







