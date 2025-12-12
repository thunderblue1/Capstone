/**
 * CuriousBooks Logging Server
 * Express server with comprehensive logging capabilities
 */

const express = require('express');
const cors = require('cors');
const logger = require('./logger');

const app = express();
const PORT = process.env.LOG_SERVER_PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Request ID middleware
app.use((req, res, next) => {
  req.requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  res.setHeader('X-Request-ID', req.requestId);
  next();
});

// ============================================
// LOGGING ENDPOINTS
// ============================================

/**
 * POST /api/logs/application
 * Log application lifecycle events from frontend
 */
app.post('/api/logs/application', (req, res) => {
  const { event, message, data } = req.body;
  
  switch (event) {
    case 'STARTUP':
      logger.application.startup({ source: 'frontend', ...data });
      break;
    case 'SHUTDOWN':
      logger.application.shutdown({ source: 'frontend', ...data });
      break;
    case 'READY':
      logger.application.ready({ source: 'frontend', ...data });
      break;
    case 'WARNING':
      logger.application.warn(message, { source: 'frontend', ...data });
      break;
    case 'ERROR':
      logger.application.error(message, { source: 'frontend', ...data });
      break;
    default:
      logger.application.info(message || event, { source: 'frontend', ...data });
  }
  
  res.json({ success: true, requestId: req.requestId });
});

/**
 * POST /api/logs/error
 * Log errors from frontend
 */
app.post('/api/logs/error', (req, res) => {
  const { message, errorCode, severity, context } = req.body;
  
  const errorContext = {
    ...context,
    requestId: req.requestId,
    source: 'frontend',
    userAgent: req.get('User-Agent'),
    ip: req.ip,
  };
  
  if (severity === 'CRITICAL') {
    logger.error.critical({ message }, errorContext);
  } else if (severity === 'WARNING') {
    logger.error.warning(message, errorContext);
  } else {
    logger.error.log({ message, code: errorCode }, errorContext);
  }
  
  res.json({ success: true, requestId: req.requestId });
});

/**
 * POST /api/logs/stacktrace
 * Log stack traces from frontend
 */
app.post('/api/logs/stacktrace', (req, res) => {
  const { message, stackTrace, errorCode, component, context } = req.body;
  
  logger.stackTrace.fromString(message, stackTrace, {
    errorCode,
    component,
    requestId: req.requestId,
    source: 'frontend',
    additionalContext: context,
  });
  
  res.json({ success: true, requestId: req.requestId });
});

/**
 * POST /api/logs/config
 * Log configuration events from frontend
 */
app.post('/api/logs/config', (req, res) => {
  const { event, configName, data, error, isValid, issues } = req.body;
  
  switch (event) {
    case 'LOADED':
      logger.config.loaded(configName, { source: 'frontend', ...data });
      break;
    case 'FAILED':
      logger.config.failed(configName, { message: error }, { source: 'frontend', ...data });
      break;
    case 'VALIDATED':
      logger.config.validated(configName, isValid, issues);
      break;
    case 'CHANGED':
      logger.config.changed(configName, data);
      break;
    default:
      logger.config.loaded(configName, { event, source: 'frontend', ...data });
  }
  
  res.json({ success: true, requestId: req.requestId });
});

/**
 * POST /api/logs/database
 * Log database events (for backend use primarily)
 */
app.post('/api/logs/database', (req, res) => {
  const { event, dbName, data, error } = req.body;
  
  switch (event) {
    case 'CONNECTING':
      logger.database.connecting(dbName, data);
      break;
    case 'CONNECTED':
      logger.database.connected(dbName, data);
      break;
    case 'DISCONNECTED':
      logger.database.disconnected(dbName, data);
      break;
    case 'ERROR':
      logger.database.error(dbName, { message: error }, data);
      break;
    case 'CONNECTION_FAILURE':
      logger.database.connectionFailure(dbName, { message: error }, data);
      break;
    default:
      logger.database.connecting(dbName, { event, ...data });
  }
  
  res.json({ success: true, requestId: req.requestId });
});

/**
 * POST /api/logs/batch
 * Batch log multiple events at once
 */
app.post('/api/logs/batch', (req, res) => {
  const { logs } = req.body;
  
  if (!Array.isArray(logs)) {
    return res.status(400).json({ error: 'logs must be an array' });
  }
  
  logs.forEach((log) => {
    const { type, ...logData } = log;
    switch (type) {
      case 'application':
        logger.application.info(logData.message, logData.data);
        break;
      case 'error':
        logger.error.log({ message: logData.message }, logData.context);
        break;
      case 'stacktrace':
        logger.stackTrace.fromString(logData.message, logData.stackTrace, logData.context);
        break;
      case 'config':
        logger.config.loaded(logData.configName, logData.data);
        break;
      case 'database':
        logger.database.connecting(logData.dbName, logData.data);
        break;
    }
  });
  
  res.json({ success: true, count: logs.length, requestId: req.requestId });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error.log(err, {
    requestId: req.requestId,
    path: req.path,
    method: req.method,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
  });
  
  logger.stackTrace.capture(err, {
    component: 'express',
    requestId: req.requestId,
  });
  
  res.status(500).json({ error: 'Internal server error', requestId: req.requestId });
});

// Start server
const server = app.listen(PORT, () => {
  logger.application.startup({
    port: PORT,
    environment: process.env.NODE_ENV || 'development',
  });
  
  logger.config.loaded('server', {
    port: PORT,
    corsEnabled: true,
    jsonLimit: '10mb',
  });
  
  console.log(`📝 Logging server running on http://localhost:${PORT}`);
  logger.application.ready({ port: PORT });
});

// Graceful shutdown
const shutdown = (signal) => {
  console.log(`\n${signal} received. Shutting down gracefully...`);
  logger.application.shutdown({ signal, reason: 'graceful_shutdown' });
  
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
  
  // Force close after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

module.exports = app;



