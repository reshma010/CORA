const { sendError } = require('../utils/response');

// Middleware to check if user is admin
const adminOnly = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    return sendError(res, 'Access denied. Admin privileges required.', 403);
  }
};

module.exports = adminOnly;