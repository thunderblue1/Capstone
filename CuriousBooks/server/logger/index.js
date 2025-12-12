/**
 * CuriousBooks Logging System
 * Centralized logging with Winston for file-based logging
 */

const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Ensure logs directory exists
const logsDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Custom format for structured JSON logging
const structuredFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Custom format for readable console output
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
    return `[${timestamp}] ${level}: ${message} ${metaStr}`;
  })
);

// ============================================
// APPLICATION LOGGER (startup/shutdown events)
// ============================================
const applicationLogger = winston.createLogger({
  level: 'info',
  format: structuredFormat,
  defaultMeta: { service: 'curiousbooks', logType: 'application' },
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'application.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true,
    }),
    new winston.transports.File({
      filename: path.join(logsDir, 'application-error.log'),
      level: 'error',
      maxsize: 5242880,
      maxFiles: 5,
    }),
  ],
});

// ============================================
// ERROR LOGGER (server errors and exceptions)
// ============================================
const errorLogger = winston.createLogger({
  level: 'error',
  format: structuredFormat,
  defaultMeta: { service: 'curiousbooks', logType: 'error' },
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 10,
      tailable: true,
    }),
  ],
});

// ============================================
// STACK TRACE LOGGER (failure stack traces)
// ============================================
const stackTraceLogger = winston.createLogger({
  level: 'error',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
      return JSON.stringify({
        timestamp,
        level,
        message,
        stackTrace: stack || meta.stackTrace || 'No stack trace available',
        errorCode: meta.errorCode || 'UNKNOWN',
        component: meta.component || 'unknown',
        userId: meta.userId || null,
        requestId: meta.requestId || null,
        additionalContext: meta.context || {},
      });
    })
  ),
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'stacktrace.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 10,
      tailable: true,
    }),
  ],
});

// ============================================
// CONFIG LOGGER (configuration loading)
// ============================================
const configLogger = winston.createLogger({
  level: 'info',
  format: structuredFormat,
  defaultMeta: { service: 'curiousbooks', logType: 'configuration' },
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'config.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 3,
      tailable: true,
    }),
  ],
});

// ============================================
// DATABASE LOGGER (connection events)
// ============================================
const databaseLogger = winston.createLogger({
  level: 'info',
  format: structuredFormat,
  defaultMeta: { service: 'curiousbooks', logType: 'database' },
  transports: [
    new winston.transports.File({
      filename: path.join(logsDir, 'database.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true,
    }),
    new winston.transports.File({
      filename: path.join(logsDir, 'database-error.log'),
      level: 'error',
      maxsize: 5242880,
      maxFiles: 5,
    }),
  ],
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production') {
  const consoleTransport = new winston.transports.Console({ format: consoleFormat });
  applicationLogger.add(consoleTransport);
  errorLogger.add(consoleTransport);
  configLogger.add(consoleTransport);
  databaseLogger.add(consoleTransport);
}

// ============================================
// LOGGER API
// ============================================

const logger = {
  /**
   * Log application lifecycle events (startup, shutdown)
   */
  application: {
    startup: (data = {}) => {
      applicationLogger.info('Application starting', {
        event: 'STARTUP',
        environment: process.env.NODE_ENV || 'development',
        nodeVersion: process.version,
        pid: process.pid,
        ...data,
      });
    },
    shutdown: (data = {}) => {
      applicationLogger.info('Application shutting down', {
        event: 'SHUTDOWN',
        uptime: process.uptime(),
        ...data,
      });
    },
    ready: (data = {}) => {
      applicationLogger.info('Application ready', {
        event: 'READY',
        ...data,
      });
    },
    info: (message, data = {}) => {
      applicationLogger.info(message, { event: 'INFO', ...data });
    },
    warn: (message, data = {}) => {
      applicationLogger.warn(message, { event: 'WARNING', ...data });
    },
    error: (message, data = {}) => {
      applicationLogger.error(message, { event: 'ERROR', ...data });
    },
  },

  /**
   * Log server errors and exceptions
   */
  error: {
    log: (error, context = {}) => {
      errorLogger.error(error.message || error, {
        errorName: error.name || 'Error',
        errorCode: context.errorCode || error.code || 'UNKNOWN',
        statusCode: context.statusCode || 500,
        path: context.path || null,
        method: context.method || null,
        userId: context.userId || null,
        requestId: context.requestId || null,
        userAgent: context.userAgent || null,
        ip: context.ip || null,
        timestamp: new Date().toISOString(),
      });
    },
    critical: (error, context = {}) => {
      errorLogger.error(error.message || error, {
        severity: 'CRITICAL',
        errorName: error.name || 'CriticalError',
        ...context,
      });
    },
    warning: (message, context = {}) => {
      errorLogger.warn(message, {
        severity: 'WARNING',
        ...context,
      });
    },
  },

  /**
   * Log stack traces for failures
   */
  stackTrace: {
    capture: (error, context = {}) => {
      stackTraceLogger.error(error.message || 'Unknown error', {
        stack: error.stack,
        stackTrace: error.stack,
        errorCode: error.code || context.errorCode || 'UNKNOWN',
        component: context.component || 'unknown',
        userId: context.userId || null,
        requestId: context.requestId || null,
        context: context.additionalContext || {},
      });
    },
    fromString: (message, stackString, context = {}) => {
      stackTraceLogger.error(message, {
        stackTrace: stackString,
        ...context,
      });
    },
  },

  /**
   * Log configuration loading events
   */
  config: {
    loaded: (configName, data = {}) => {
      configLogger.info(`Configuration loaded: ${configName}`, {
        event: 'CONFIG_LOADED',
        configName,
        status: 'SUCCESS',
        ...data,
      });
    },
    failed: (configName, error, data = {}) => {
      configLogger.error(`Configuration failed: ${configName}`, {
        event: 'CONFIG_FAILED',
        configName,
        status: 'FAILURE',
        error: error.message || error,
        ...data,
      });
    },
    validated: (configName, isValid, issues = []) => {
      const level = isValid ? 'info' : 'warn';
      configLogger[level](`Configuration validated: ${configName}`, {
        event: 'CONFIG_VALIDATED',
        configName,
        isValid,
        issues,
      });
    },
    changed: (configName, changes = {}) => {
      configLogger.info(`Configuration changed: ${configName}`, {
        event: 'CONFIG_CHANGED',
        configName,
        changes,
      });
    },
  },

  /**
   * Log database connection events
   */
  database: {
    connecting: (dbName, data = {}) => {
      databaseLogger.info(`Connecting to database: ${dbName}`, {
        event: 'DB_CONNECTING',
        database: dbName,
        status: 'CONNECTING',
        ...data,
      });
    },
    connected: (dbName, data = {}) => {
      databaseLogger.info(`Connected to database: ${dbName}`, {
        event: 'DB_CONNECTED',
        database: dbName,
        status: 'CONNECTED',
        connectionTime: data.connectionTime || null,
        ...data,
      });
    },
    disconnected: (dbName, data = {}) => {
      databaseLogger.warn(`Disconnected from database: ${dbName}`, {
        event: 'DB_DISCONNECTED',
        database: dbName,
        status: 'DISCONNECTED',
        ...data,
      });
    },
    error: (dbName, error, data = {}) => {
      databaseLogger.error(`Database error: ${dbName}`, {
        event: 'DB_ERROR',
        database: dbName,
        status: 'ERROR',
        errorMessage: error.message || error,
        errorCode: error.code || 'UNKNOWN',
        ...data,
      });
    },
    connectionFailure: (dbName, error, data = {}) => {
      databaseLogger.error(`Database connection failure: ${dbName}`, {
        event: 'DB_CONNECTION_FAILURE',
        database: dbName,
        status: 'CONNECTION_FAILED',
        errorMessage: error.message || error,
        errorCode: error.code || 'UNKNOWN',
        retryCount: data.retryCount || 0,
        maxRetries: data.maxRetries || null,
        ...data,
      });
    },
    query: (dbName, query, duration, data = {}) => {
      databaseLogger.debug(`Database query: ${dbName}`, {
        event: 'DB_QUERY',
        database: dbName,
        query: query.substring(0, 500), // Truncate long queries
        duration,
        ...data,
      });
    },
    poolStatus: (dbName, status) => {
      databaseLogger.info(`Database pool status: ${dbName}`, {
        event: 'DB_POOL_STATUS',
        database: dbName,
        ...status,
      });
    },
  },
};

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error.critical(error, { type: 'UNCAUGHT_EXCEPTION' });
  logger.stackTrace.capture(error, { component: 'process', errorCode: 'UNCAUGHT_EXCEPTION' });
  console.error('Uncaught Exception:', error);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  const error = reason instanceof Error ? reason : new Error(String(reason));
  logger.error.critical(error, { type: 'UNHANDLED_REJECTION' });
  logger.stackTrace.capture(error, { component: 'process', errorCode: 'UNHANDLED_REJECTION' });
  console.error('Unhandled Rejection:', reason);
});

module.exports = logger;
module.exports.applicationLogger = applicationLogger;
module.exports.errorLogger = errorLogger;
module.exports.stackTraceLogger = stackTraceLogger;
module.exports.configLogger = configLogger;
module.exports.databaseLogger = databaseLogger;



