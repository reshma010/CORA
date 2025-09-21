# CORA Backend API

A Node.js MongoDB backend API server built with Express.js, featuring user authentication, CRUD operations, and comprehensive middleware.

##  Features

- **Express.js Framework**: Fast and minimal web framework
- **MongoDB Integration**: Using Mongoose ODM for database operations
- **JWT Authentication**: Secure user authentication and authorization
- **Input Validation**: Request validation using express-validator
- **Security Middleware**: Helmet, CORS, and rate limiting
- **Error Handling**: Centralized error handling middleware
- **Environment Configuration**: Environment-based settings
- **API Documentation**: RESTful API with consistent response format

##  Prerequisites

- Node.js (version 16 or higher)
- MongoDB (local installation or MongoDB Atlas)
- npm or yarn package manager

##  Installation

1. **Clone and navigate to the project:**
   ```bash
   cd "CORA BACKEND"
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment Setup:**
   - Copy `.env.example` to `.env`
   - Update the environment variables:
   ```bash
   cp .env.example .env
   ```

4. **Configure Environment Variables:**
   ```env
   NODE_ENV=development
   PORT=5001
   MONGODB_URI=mongodb://localhost:27017/cora_db
   JWT_SECRET=secure-jwt-key-change-this-in-production
   JWT_EXPIRE=7d
   CORS_ORIGIN=http://localhost:3000
   ```

##  Running the Application

### Development Mode (with auto-restart):
```bash
npm run dev
```

### Production Mode:
```bash
npm start
```

The server starts on `http://localhost:5001` 

##  Security Features

- **Helmet**: Sets security-related HTTP headers
- **CORS**: Configurable Cross-Origin Resource Sharing
- **Rate Limiting**: Prevents brute force attacks
- **Input Validation**: Validates and sanitizes user input
- **Password Hashing**: Bcrypt for secure password storage
- **JWT Authentication**: Stateless authentication tokens

##  API Endpoints

### Health Check
- **GET** `/health` - Server health status
- **GET** `/api` - API information

### Authentication Routes (`/api/auth`)
- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - User login
- **GET** `/api/auth/me` - Get current user profile (Protected)

### User Routes (`/api/users`)
- **GET** `/api/users` - Get all users (Admin only)
- **GET** `/api/users/:id` - Get single user (Protected)
- **PUT** `/api/users/:id` - Update user profile (Protected)
- **DELETE** `/api/users/:id` - Delete user (Admin only)

##  API Usage Examples

### Register a new user:
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Login:
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Get user profile (requires token):
```bash
curl -X GET http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

##  Response Format

All API responses follow this consistent format:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

##  Project Structure

```
CORA BACKEND/
├── .github/
│   └── project-instructions.md    # Project instructions
├── src/
│   ├── config/
│   │   └── database.js            # MongoDB connection
│   ├── controllers/
│   │   ├── authController.js      # Authentication logic
│   │   └── userController.js      # User CRUD operations
│   ├── middleware/
│   │   ├── auth.js               # JWT authentication middleware
│   │   ├── adminOnly.js          # Admin authorization middleware
│   │   └── errorHandler.js       # Global error handler
│   ├── models/
│   │   └── User.js               # User schema and methods
│   ├── routes/
│   │   ├── auth.js               # Authentication routes
│   │   └── users.js              # User routes
│   └── utils/
│       └── response.js           # Response utilities
├── .env                          # Environment variables
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
├── package.json                  # Dependencies and scripts
└── server.js                     # Main server file
```

##  Development

### Adding New Routes:
1. Create controller in `src/controllers/`
2. Create route file in `src/routes/`
3. Add route to `server.js`

### Adding New Models:
1. Create model in `src/models/`
2. Import and use in controllers

### Adding Middleware:
1. Create middleware in `src/middleware/`
2. Apply in routes or globally in `server.js`

##  Testing the API

API testing methods include:
- **Postman**: Import the endpoints
- **curl**: Command-line testing (examples above)
- **Thunder Client**: VS Code extension
- **REST Client**: VS Code extension

##  Troubleshooting

### Common Issues:

1. **Port already in use**: Change PORT in `.env`
2. **MongoDB connection failed**: Ensure MongoDB is running
3. **Authentication errors**: Check JWT_SECRET in `.env`
4. **CORS errors**: Update CORS_ORIGIN in `.env`

### Logs:
The server logs all important events to the console. Check the terminal for detailed error messages.

##  License

This project is licensed under the ISC License.

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

---

**Server Status**:  Running on http://localhost:5001