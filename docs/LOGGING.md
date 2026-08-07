# CuriousBooks Logging System Documentation

## Overview

The CuriousBooks logging system provides comprehensive file-based logging for application events, errors, stack traces, configuration, and database operations. Logs are written to the `logs/` directory in JSON format for easy parsing and analysis.

## Log Files

| File Name | Purpose | Max Size | Max Files |
|-----------|---------|----------|-----------|
| `application.log` | Application lifecycle events (startup, shutdown, general info) | 5 MB | 5 |
| `application-error.log` | Application-level errors only | 5 MB | 5 |
| `error.log` | Server errors and exceptions | 10 MB | 10 |
| `stacktrace.log` | Full stack traces for failures | 10 MB | 10 |
| `config.log` | Configuration loading and validation events | 5 MB | 3 |
| `database.log` | Database connection and query events | 5 MB | 5 |
| `database-error.log` | Database errors only | 5 MB | 5 |

---

## Log File Structures

### 1. Application Log (`application.log`)

**Purpose:** Tracks application startup, shutdown, and general lifecycle events.

#### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2025-12-10T14:30:45.123Z"` |
| `level` | string | Log level (info, warn, error) | `"info"` |
| `message` | string | Human-readable description | `"Application starting"` |
| `service` | string | Service identifier | `"curiousbooks"` |
| `logType` | string | Log category | `"application"` |
| `event` | string | Event type code | `"STARTUP"` |
| `environment` | string | Runtime environment | `"development"` |
| `nodeVersion` | string | Node.js version | `"v20.10.0"` |
| `pid` | number | Process ID | `12345` |
| `port` | number | Server port (if applicable) | `5001` |
| `source` | string | Origin of log (backend/frontend) | `"frontend"` |
| `uptime` | number | Process uptime in seconds | `3600.5` |

#### Example Entries

**Application Startup:**
```json
{
  "timestamp": "2025-12-10T14:30:45.123Z",
  "level": "info",
  "message": "Application starting",
  "service": "curiousbooks",
  "logType": "application",
  "event": "STARTUP",
  "environment": "development",
  "nodeVersion": "v20.10.0",
  "pid": 12345,
  "port": 5001
}
```

**Application Ready:**
```json
{
  "timestamp": "2025-12-10T14:30:46.456Z",
  "level": "info",
  "message": "Application ready",
  "service": "curiousbooks",
  "logType": "application",
  "event": "READY",
  "port": 5001,
  "loadTime": 1234.56
}
```

**Application Shutdown:**
```json
{
  "timestamp": "2025-12-10T18:45:30.789Z",
  "level": "info",
  "message": "Application shutting down",
  "service": "curiousbooks",
  "logType": "application",
  "event": "SHUTDOWN",
  "uptime": 15285.666,
  "signal": "SIGTERM",
  "reason": "graceful_shutdown"
}
```

---

### 2. Error Log (`error.log`)

**Purpose:** Captures server errors and exceptions with contextual information.

#### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2025-12-10T14:35:22.456Z"` |
| `level` | string | Always "error" | `"error"` |
| `message` | string | Error message | `"Failed to fetch user data"` |
| `service` | string | Service identifier | `"curiousbooks"` |
| `logType` | string | Log category | `"error"` |
| `errorName` | string | Error class name | `"ApiError"` |
| `errorCode` | string | Application error code | `"USER_NOT_FOUND"` |
| `statusCode` | number | HTTP status code | `404` |
| `path` | string | Request path | `"/api/users/123"` |
| `method` | string | HTTP method | `"GET"` |
| `userId` | string/null | User ID if authenticated | `"user_abc123"` |
| `requestId` | string | Unique request identifier | `"req_1702218922_a1b2c3d4e"` |
| `userAgent` | string | Client user agent | `"Mozilla/5.0..."` |
| `ip` | string | Client IP address | `"192.168.1.100"` |
| `severity` | string | Error severity level | `"CRITICAL"` |

#### Example Entries

**Standard Error:**
```json
{
  "timestamp": "2025-12-10T14:35:22.456Z",
  "level": "error",
  "message": "Failed to fetch user data",
  "service": "curiousbooks",
  "logType": "error",
  "errorName": "ApiError",
  "errorCode": "USER_NOT_FOUND",
  "statusCode": 404,
  "path": "/api/users/123",
  "method": "GET",
  "userId": null,
  "requestId": "req_1702218922_a1b2c3d4e",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "ip": "192.168.1.100"
}
```

**Critical Error:**
```json
{
  "timestamp": "2025-12-10T14:40:15.789Z",
  "level": "error",
  "message": "Payment processing failed",
  "service": "curiousbooks",
  "logType": "error",
  "severity": "CRITICAL",
  "errorName": "PaymentError",
  "errorCode": "PAYMENT_GATEWAY_UNAVAILABLE",
  "statusCode": 503,
  "path": "/api/orders/checkout",
  "method": "POST",
  "userId": "user_xyz789",
  "requestId": "req_1702219215_f5g6h7i8j"
}
```

---

### 3. Stack Trace Log (`stacktrace.log`)

**Purpose:** Stores detailed stack traces for debugging failures.

#### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2025-12-10T14:42:33.123Z"` |
| `level` | string | Always "error" | `"error"` |
| `message` | string | Error message | `"Cannot read property 'id' of undefined"` |
| `stackTrace` | string | Full stack trace | `"TypeError: Cannot read property..."` |
| `errorCode` | string | Application error code | `"UNCAUGHT_EXCEPTION"` |
| `component` | string | Component where error occurred | `"BookSynopsisPage"` |
| `userId` | string/null | User ID if available | `"user_abc123"` |
| `requestId` | string/null | Request ID if available | `"req_1702219353_k9l0m1n2o"` |
| `additionalContext` | object | Extra debugging info | `{"bookId": "123"}` |

#### Example Entry

```json
{
  "timestamp": "2025-12-10T14:42:33.123Z",
  "level": "error",
  "message": "Cannot read property 'id' of undefined",
  "stackTrace": "TypeError: Cannot read property 'id' of undefined\n    at BookCard (webpack://curiousbooks/./src/components/BookCard/BookCard.tsx:45:23)\n    at renderWithHooks (webpack://curiousbooks/./node_modules/react-dom/cjs/react-dom.development.js:14985:18)\n    at mountIndeterminateComponent (webpack://curiousbooks/./node_modules/react-dom/cjs/react-dom.development.js:17811:13)\n    at beginWork (webpack://curiousbooks/./node_modules/react-dom/cjs/react-dom.development.js:19049:16)\n    at HTMLUnknownElement.callCallback (webpack://curiousbooks/./node_modules/react-dom/cjs/react-dom.development.js:3945:14)",
  "errorCode": "UNCAUGHT_EXCEPTION",
  "component": "BookCard",
  "userId": null,
  "requestId": null,
  "additionalContext": {
    "bookId": undefined,
    "url": "http://localhost:3000/book/undefined"
  }
}
```

---

### 4. Configuration Log (`config.log`)

**Purpose:** Tracks configuration loading, validation, and changes.

#### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2025-12-10T14:30:45.001Z"` |
| `level` | string | Log level | `"info"` |
| `message` | string | Description | `"Configuration loaded: database"` |
| `service` | string | Service identifier | `"curiousbooks"` |
| `logType` | string | Log category | `"configuration"` |
| `event` | string | Event type | `"CONFIG_LOADED"` |
| `configName` | string | Configuration name | `"database"` |
| `status` | string | Load status | `"SUCCESS"` |
| `isValid` | boolean | Validation result | `true` |
| `issues` | array | Validation issues | `["Missing API key"]` |
| `changes` | object | Configuration changes | `{"timeout": {"old": 5000, "new": 10000}}` |

#### Example Entries

**Configuration Loaded:**
```json
{
  "timestamp": "2025-12-10T14:30:45.001Z",
  "level": "info",
  "message": "Configuration loaded: database",
  "service": "curiousbooks",
  "logType": "configuration",
  "event": "CONFIG_LOADED",
  "configName": "database",
  "status": "SUCCESS",
  "host": "localhost",
  "port": 5432,
  "database": "curiousbooks_db",
  "ssl": false
}
```

**Configuration Failed:**
```json
{
  "timestamp": "2025-12-10T14:30:45.002Z",
  "level": "error",
  "message": "Configuration failed: payment-gateway",
  "service": "curiousbooks",
  "logType": "configuration",
  "event": "CONFIG_FAILED",
  "configName": "payment-gateway",
  "status": "FAILURE",
  "error": "Missing required environment variable: STRIPE_SECRET_KEY"
}
```

**Configuration Validated:**
```json
{
  "timestamp": "2025-12-10T14:30:45.003Z",
  "level": "warn",
  "message": "Configuration validated: email",
  "service": "curiousbooks",
  "logType": "configuration",
  "event": "CONFIG_VALIDATED",
  "configName": "email",
  "isValid": false,
  "issues": [
    "SMTP host not configured",
    "Email sender address missing"
  ]
}
```

---

### 5. Database Log (`database.log`)

**Purpose:** Monitors database connections, disconnections, and errors.

#### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2025-12-10T14:30:46.100Z"` |
| `level` | string | Log level | `"info"` |
| `message` | string | Description | `"Connected to database: main"` |
| `service` | string | Service identifier | `"curiousbooks"` |
| `logType` | string | Log category | `"database"` |
| `event` | string | Event type | `"DB_CONNECTED"` |
| `database` | string | Database name | `"main"` |
| `status` | string | Connection status | `"CONNECTED"` |
| `connectionTime` | number | Connection time in ms | `245` |
| `errorMessage` | string | Error details | `"Connection refused"` |
| `errorCode` | string | Database error code | `"ECONNREFUSED"` |
| `retryCount` | number | Retry attempt number | `3` |
| `maxRetries` | number | Maximum retry attempts | `5` |

#### Example Entries

**Database Connecting:**
```json
{
  "timestamp": "2025-12-10T14:30:46.100Z",
  "level": "info",
  "message": "Connecting to database: main",
  "service": "curiousbooks",
  "logType": "database",
  "event": "DB_CONNECTING",
  "database": "main",
  "status": "CONNECTING",
  "host": "localhost",
  "port": 5432
}
```

**Database Connected:**
```json
{
  "timestamp": "2025-12-10T14:30:46.345Z",
  "level": "info",
  "message": "Connected to database: main",
  "service": "curiousbooks",
  "logType": "database",
  "event": "DB_CONNECTED",
  "database": "main",
  "status": "CONNECTED",
  "connectionTime": 245,
  "poolSize": 10
}
```

**Database Connection Failure:**
```json
{
  "timestamp": "2025-12-10T14:30:51.567Z",
  "level": "error",
  "message": "Database connection failure: main",
  "service": "curiousbooks",
  "logType": "database",
  "event": "DB_CONNECTION_FAILURE",
  "database": "main",
  "status": "CONNECTION_FAILED",
  "errorMessage": "Connection refused",
  "errorCode": "ECONNREFUSED",
  "retryCount": 3,
  "maxRetries": 5,
  "host": "localhost",
  "port": 5432
}
```

**Database Disconnected:**
```json
{
  "timestamp": "2025-12-10T18:45:30.100Z",
  "level": "warn",
  "message": "Disconnected from database: main",
  "service": "curiousbooks",
  "logType": "database",
  "event": "DB_DISCONNECTED",
  "database": "main",
  "status": "DISCONNECTED",
  "reason": "graceful_shutdown",
  "activeConnections": 0
}
```

---

## Usage Examples

### Backend (Node.js)

```javascript
const logger = require('./server/logger');

// Application startup
logger.application.startup({
  port: 5000,
  environment: 'production'
});

// Log an error
try {
  await someOperation();
} catch (error) {
  logger.error.log(error, {
    component: 'OrderService',
    errorCode: 'ORDER_CREATION_FAILED',
    userId: currentUser.id
  });
  
  // Also capture stack trace
  logger.stackTrace.capture(error, {
    component: 'OrderService',
    errorCode: 'ORDER_CREATION_FAILED'
  });
}

// Configuration loading
logger.config.loaded('database', {
  host: 'localhost',
  port: 5432
});

// Database connection
logger.database.connecting('main', { host: 'localhost' });
logger.database.connected('main', { connectionTime: 245 });
logger.database.connectionFailure('main', error, { retryCount: 3 });

// Application shutdown
logger.application.shutdown({ signal: 'SIGTERM' });
```

### Frontend (React/TypeScript)

```typescript
import { logger } from './services/logger';

// Application startup (in main.tsx)
logger.application.startup({
  appName: 'CuriousBooks',
  version: '1.0.0'
});

// Component error handling
useEffect(() => {
  const loadData = async () => {
    try {
      const data = await api.getData();
      logger.application.info('Data loaded', { count: data.length });
    } catch (error) {
      logger.error.log(error, {
        component: 'MyComponent',
        errorCode: 'DATA_LOAD_ERROR'
      });
    }
  };
  loadData();
}, []);

// Configuration changes
logger.config.loaded('user-preferences', {
  theme: 'dark',
  language: 'en'
});
```

---

## Log Rotation

All log files are automatically rotated based on:
- **Maximum file size**: When a log file reaches its max size, it's rotated
- **Maximum number of files**: Older rotated files are deleted when limit is reached

Rotated files follow the naming convention: `filename.log.1`, `filename.log.2`, etc.

---

## Environment Configuration

Set these environment variables to configure logging:

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `development` | Environment (affects console output) |
| `LOG_SERVER_PORT` | `5001` | Port for logging server |
| `VITE_LOG_SERVER_URL` | `http://localhost:5001` | Frontend logging endpoint |

---

## Starting the Logging Server

```bash
cd server
npm install
npm start
```

The logging server will start on port 5001 (default) and create the `logs/` directory automatically.



