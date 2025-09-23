// Istiaq Hossain
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const connectDB = require('./src/config/database');
const errorHandler = require('./src/middleware/errorHandler');
const { sendSuccess } = require('./src/utils/response');

// Connect to MongoDB
connectDB();

const app = express();

// Security middleware
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // limit each IP to 100 requests per windowMs
  message: {
    success: false,
    message: 'Too many requests from this IP, try again later.',
    timestamp: new Date().toISOString()
  }
});

app.use(limiter);

// CORS configuration
const corsOptions = {
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true,
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

// Static file serving
app.use(express.static('public'));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`\n REQUEST: ${req.method} ${req.originalUrl}`);
  console.log(` TIME: ${new Date().toISOString()}`);
  console.log(` USER-AGENT: ${req.get('User-Agent') || 'Unknown'}`);
  console.log(` CONTENT-TYPE: ${req.get('Content-Type') || 'None'}`);
  console.log(` CONTENT-LENGTH: ${req.get('Content-Length') || 'Unknown'}`);
  next();
});

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Root route - CORA API Welcome
app.get('/', (req, res) => {
  sendSuccess(res, 'Welcome to CORA API', {
    version: '1.0.0',
    status: 'Server is running',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    endpoints: {
      health: '/health',
      api: '/api',
      auth: '/api/auth',
      users: '/api/users',
      robots: '/api/robots',
      robot_detections: '/api/detections'
    },
    documentation: 'See /api for more details'
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  sendSuccess(res, 'Server is running', {
    status: 'OK',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.get('/api', (req, res) => {
  sendSuccess(res, 'CORA API is running', {
    version: '1.0.0',
    endpoints: {
      health: '/health',
      api: '/api',
      auth: '/api/auth',
      users: '/api/users',
      robots: '/api/robots',
      robot_detections: '/api/detections',
      robot_active: '/api/detections/active'
    }
  });
});

// API Routes
app.use('/api/auth', require('./src/routes/auth'));
app.use('/api/users', require('./src/routes/users'));
// Mount robot detection routes at dedicated path (no auth required for robots)
app.use('/api/detections', require('./src/routes/detections'));
app.use('/api/robots', require('./src/routes/robots'));

// Error handling middleware (must be last)
app.use(errorHandler);

// 404 handler for unmatched routes
app.use('*', (req, res) => {
  console.log(` 404 ERROR: ${req.method} ${req.originalUrl} not found`);
  console.log(' Available routes: /, /health, /api, /api/auth, /api/users, /api/robots, /api/detections');
  
  res.status(404).json({
    success: false,
    message: `Route ${req.method} ${req.originalUrl} not found`,
    availableRoutes: [
      'GET /',
      'GET /health', 
      'GET /api',
      'POST /api/auth/register',
      'POST /api/auth/login',
      'POST /api/auth/forgot-password',
      'GET /api/auth/reset-password/:token',
      'POST /api/auth/reset-password/:token',
      'GET /api/users',
      'GET /api/robots'
    ],
    timestamp: new Date().toISOString()
  });
});

// Ensure the server binds to the correct port for Render
const PORT = process.env.PORT || 5001;

// Start server with proper port binding for deployment
app.listen(PORT, '0.0.0.0', () => {
  console.log(` CORA Server running in ${process.env.NODE_ENV || 'development'} mode`);
  console.log(` Server listening on port ${PORT}`);
  console.log(` Available at: http://localhost:${PORT}`);
  console.log(` Health check: http://localhost:${PORT}/health`);
  console.log(` API endpoints: http://localhost:${PORT}/api`);
});