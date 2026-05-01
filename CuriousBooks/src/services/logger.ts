/**
 * CuriousBooks Frontend Logger
 * Client-side logging service that sends logs to the logging server
 */

// Configuration
const LOG_SERVER_URL = import.meta.env.VITE_LOG_SERVER_URL || 'http://localhost:5001';
const ENABLE_CONSOLE_LOGS = import.meta.env.DEV;
const BATCH_SIZE = 10;
const BATCH_INTERVAL = 5000; // 5 seconds

// Types
interface LogEntry {
  type: 'application' | 'error' | 'stacktrace' | 'config' | 'database';
  timestamp: string;
  [key: string]: unknown;
}

interface ApplicationLogData {
  event?: string;
  message?: string;
  data?: Record<string, unknown>;
}

interface ErrorLogData {
  message: string;
  errorCode?: string;
  severity?: 'ERROR' | 'WARNING' | 'CRITICAL';
  context?: Record<string, unknown>;
}

interface StackTraceLogData {
  message: string;
  stackTrace: string;
  errorCode?: string;
  component?: string;
  context?: Record<string, unknown>;
}

interface ConfigLogData {
  event: 'LOADED' | 'FAILED' | 'VALIDATED' | 'CHANGED';
  configName: string;
  data?: Record<string, unknown>;
  error?: string;
  isValid?: boolean;
  issues?: string[];
}

interface DatabaseLogData {
  event: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR' | 'CONNECTION_FAILURE';
  dbName: string;
  data?: Record<string, unknown>;
  error?: string;
}

// Log queue for batching
let logQueue: LogEntry[] = [];
let batchTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * Send logs to the server
 */
async function sendLogs(endpoint: string, data: object): Promise<void> {
  try {
    const response = await fetch(`${LOG_SERVER_URL}/api/logs/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...(data as Record<string, unknown>),
        clientTimestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    });

    if (!response.ok) {
      // Only warn in development, fail silently in production
      if (ENABLE_CONSOLE_LOGS) {
        console.warn(`Failed to send log to ${endpoint}:`, response.status);
      }
    }
  } catch (error) {
    // Fail silently to avoid recursive logging and console spam
    // Only log connection errors once to avoid spam
    if (ENABLE_CONSOLE_LOGS && !(error instanceof TypeError && error.message.includes('fetch'))) {
      console.warn('Logger: Failed to send log to server:', error);
    }
  }
}

/**
 * Send batched logs
 */
async function sendBatchedLogs(): Promise<void> {
  if (logQueue.length === 0) return;

  const logsToSend = [...logQueue];
  logQueue = [];

  try {
    await fetch(`${LOG_SERVER_URL}/api/logs/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ logs: logsToSend }),
    });
  } catch (error) {
    // Fail silently - logging server may not be running
    // Only log non-network errors to avoid spam
    if (ENABLE_CONSOLE_LOGS && !(error instanceof TypeError && error.message.includes('fetch'))) {
      console.warn('Logger: Failed to send batched logs:', error);
    }
  }
}

/**
 * Add log to queue for batching
 */
function queueLog(entry: LogEntry): void {
  logQueue.push(entry);

  if (logQueue.length >= BATCH_SIZE) {
    sendBatchedLogs();
  } else if (!batchTimer) {
    batchTimer = setTimeout(() => {
      sendBatchedLogs();
      batchTimer = null;
    }, BATCH_INTERVAL);
  }
}

/**
 * Get browser/environment info
 */
function getEnvironmentInfo(): Record<string, unknown> {
  return {
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    screenResolution: `${window.screen.width}x${window.screen.height}`,
    viewportSize: `${window.innerWidth}x${window.innerHeight}`,
    url: window.location.href,
    referrer: document.referrer || null,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Extract stack trace from error
 */
function extractStackTrace(error: Error | unknown): string {
  if (error instanceof Error && error.stack) {
    return error.stack;
  }
  if (typeof error === 'string') {
    return error;
  }
  try {
    return new Error().stack || 'No stack trace available';
  } catch {
    return 'Unable to capture stack trace';
  }
}

// ============================================
// LOGGER API
// ============================================

export const logger = {
  /**
   * Application lifecycle logging
   */
  application: {
    startup: (data: Record<string, unknown> = {}) => {
      const logData: ApplicationLogData = {
        event: 'STARTUP',
        message: 'Frontend application starting',
        data: {
          ...getEnvironmentInfo(),
          ...data,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log('🚀 Application starting', logData.data);
      }

      sendLogs('application', logData);
    },

    shutdown: (data: Record<string, unknown> = {}) => {
      const logData: ApplicationLogData = {
        event: 'SHUTDOWN',
        message: 'Frontend application shutting down',
        data: {
          sessionDuration: performance.now(),
          ...data,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log('👋 Application shutting down', logData.data);
      }

      // Use sendBeacon for reliability during page unload
      const blob = new Blob([JSON.stringify(logData)], { type: 'application/json' });
      navigator.sendBeacon(`${LOG_SERVER_URL}/api/logs/application`, blob);
    },

    ready: (data: Record<string, unknown> = {}) => {
      const logData: ApplicationLogData = {
        event: 'READY',
        message: 'Frontend application ready',
        data: {
          loadTime: performance.now(),
          ...data,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log('✅ Application ready', logData.data);
      }

      sendLogs('application', logData);
    },

    info: (message: string, data: Record<string, unknown> = {}) => {
      if (ENABLE_CONSOLE_LOGS) {
        console.info(`ℹ️ ${message}`, data);
      }

      sendLogs('application', { event: 'INFO', message, data });
    },

    warn: (message: string, data: Record<string, unknown> = {}) => {
      if (ENABLE_CONSOLE_LOGS) {
        console.warn(`⚠️ ${message}`, data);
      }

      sendLogs('application', { event: 'WARNING', message, data });
    },
  },

  /**
   * Error logging
   */
  error: {
    log: (error: unknown, context: Record<string, unknown> = {}) => {
      const message =
        error instanceof Error
          ? error.message
          : typeof error === 'string'
            ? error
            : String(error);
      const errorCode = context.errorCode as string || 'FRONTEND_ERROR';

      const logData: ErrorLogData = {
        message,
        errorCode,
        severity: 'ERROR',
        context: {
          ...getEnvironmentInfo(),
          ...context,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`❌ ${message}`, context);
      }

      sendLogs('error', logData);

      // Also capture stack trace if available
      if (error instanceof Error && error.stack) {
        logger.stackTrace.capture(error, context);
      }
    },

    critical: (error: unknown, context: Record<string, unknown> = {}) => {
      const message =
        error instanceof Error
          ? error.message
          : typeof error === 'string'
            ? error
            : String(error);

      const logData: ErrorLogData = {
        message,
        errorCode: context.errorCode as string || 'CRITICAL_ERROR',
        severity: 'CRITICAL',
        context: {
          ...getEnvironmentInfo(),
          ...context,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`🔥 CRITICAL: ${message}`, context);
      }

      sendLogs('error', logData);

      if (error instanceof Error && error.stack) {
        logger.stackTrace.capture(error, { ...context, severity: 'CRITICAL' });
      }
    },

    warning: (message: string, context: Record<string, unknown> = {}) => {
      const logData: ErrorLogData = {
        message,
        severity: 'WARNING',
        context: {
          ...getEnvironmentInfo(),
          ...context,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.warn(`⚠️ ${message}`, context);
      }

      sendLogs('error', logData);
    },
  },

  /**
   * Stack trace logging
   */
  stackTrace: {
    capture: (error: Error | unknown, context: Record<string, unknown> = {}) => {
      const message = error instanceof Error ? error.message : 'Unknown error';
      const stackTrace = extractStackTrace(error);

      const logData: StackTraceLogData = {
        message,
        stackTrace,
        errorCode: context.errorCode as string || 'STACK_TRACE',
        component: context.component as string || 'frontend',
        context: {
          ...getEnvironmentInfo(),
          ...context,
        },
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`📚 Stack trace captured for: ${message}\n`, stackTrace);
      }

      sendLogs('stacktrace', logData);
    },

    fromString: (message: string, stackTrace: string, context: Record<string, unknown> = {}) => {
      const logData: StackTraceLogData = {
        message,
        stackTrace,
        errorCode: context.errorCode as string || 'STACK_TRACE',
        component: context.component as string || 'frontend',
        context,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`📚 Stack trace: ${message}\n`, stackTrace);
      }

      sendLogs('stacktrace', logData);
    },
  },

  /**
   * Configuration logging
   */
  config: {
    loaded: (configName: string, data: Record<string, unknown> = {}) => {
      const logData: ConfigLogData = {
        event: 'LOADED',
        configName,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log(`⚙️ Config loaded: ${configName}`, data);
      }

      sendLogs('config', logData);
    },

    failed: (configName: string, error: string, data: Record<string, unknown> = {}) => {
      const logData: ConfigLogData = {
        event: 'FAILED',
        configName,
        error,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`⚙️ Config failed: ${configName}`, error, data);
      }

      sendLogs('config', logData);
    },

    validated: (configName: string, isValid: boolean, issues: string[] = []) => {
      const logData: ConfigLogData = {
        event: 'VALIDATED',
        configName,
        isValid,
        issues,
      };

      if (ENABLE_CONSOLE_LOGS) {
        if (isValid) {
          console.log(`⚙️ Config validated: ${configName} ✓`);
        } else {
          console.warn(`⚙️ Config validation issues: ${configName}`, issues);
        }
      }

      sendLogs('config', logData);
    },

    changed: (configName: string, changes: Record<string, unknown>) => {
      const logData: ConfigLogData = {
        event: 'CHANGED',
        configName,
        data: changes,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log(`⚙️ Config changed: ${configName}`, changes);
      }

      sendLogs('config', logData);
    },
  },

  /**
   * Database/API connection logging
   */
  database: {
    connecting: (dbName: string, data: Record<string, unknown> = {}) => {
      const logData: DatabaseLogData = {
        event: 'CONNECTING',
        dbName,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log(`🔌 Connecting to: ${dbName}`, data);
      }

      sendLogs('database', logData);
    },

    connected: (dbName: string, data: Record<string, unknown> = {}) => {
      const logData: DatabaseLogData = {
        event: 'CONNECTED',
        dbName,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.log(`✅ Connected to: ${dbName}`, data);
      }

      sendLogs('database', logData);
    },

    disconnected: (dbName: string, data: Record<string, unknown> = {}) => {
      const logData: DatabaseLogData = {
        event: 'DISCONNECTED',
        dbName,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.warn(`🔌 Disconnected from: ${dbName}`, data);
      }

      sendLogs('database', logData);
    },

    error: (dbName: string, error: string, data: Record<string, unknown> = {}) => {
      const logData: DatabaseLogData = {
        event: 'ERROR',
        dbName,
        error,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`❌ Database error (${dbName}):`, error, data);
      }

      sendLogs('database', logData);
    },

    connectionFailure: (dbName: string, error: string, data: Record<string, unknown> = {}) => {
      const logData: DatabaseLogData = {
        event: 'CONNECTION_FAILURE',
        dbName,
        error,
        data,
      };

      if (ENABLE_CONSOLE_LOGS) {
        console.error(`🔥 Connection failure (${dbName}):`, error, data);
      }

      sendLogs('database', logData);
    },
  },

  /**
   * Utility methods
   */
  utils: {
    /**
     * Flush all queued logs immediately
     */
    flush: () => {
      if (batchTimer) {
        clearTimeout(batchTimer);
        batchTimer = null;
      }
      sendBatchedLogs();
    },

    /**
     * Queue a log for batched sending
     */
    queue: (type: LogEntry['type'], data: Record<string, unknown>) => {
      queueLog({
        type,
        timestamp: new Date().toISOString(),
        ...data,
      });
    },
  },
};

// ============================================
// GLOBAL ERROR HANDLERS
// ============================================

// Capture unhandled errors
window.addEventListener('error', (event) => {
  logger.error.critical(event.error || event.message, {
    component: 'window',
    errorCode: 'UNCAUGHT_ERROR',
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
  });
});

// Capture unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  const error = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
  logger.error.critical(error, {
    component: 'window',
    errorCode: 'UNHANDLED_REJECTION',
  });
});

// Log page unload
window.addEventListener('beforeunload', () => {
  logger.application.shutdown({ reason: 'page_unload' });
});

// Log visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    logger.application.info('Application hidden', { visibility: 'hidden' });
  } else {
    logger.application.info('Application visible', { visibility: 'visible' });
  }
});

export default logger;



