const { sendServerError } = require('../utils/response');

const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message);
  console.error('Stack:', err.stack);

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    return sendServerError(res, 'Resource not found');
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return sendServerError(res, `${field} already exists`);
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const messages = Object.values(err.errors).map(val => val.message);
    return sendServerError(res, messages.join(', '));
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return sendServerError(res, 'Invalid token');
  }

  if (err.name === 'TokenExpiredError') {
    return sendServerError(res, 'Token expired');
  }

  return sendServerError(res, err.message || 'Server Error');
};

module.exports = errorHandler;