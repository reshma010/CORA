//Oleg Korobeyko
// Response utility functions
const sendResponse = (res, statusCode, success, message, data = null) => {
  const response = {
    success,
    message,
    timestamp: new Date().toISOString()
  };
  
  if (data !== null) {
    response.data = data;
  }
  
  return res.status(statusCode).json(response);
};

const sendSuccess = (res, message, data = null, statusCode = 200) => {
  return sendResponse(res, statusCode, true, message, data);
};

const sendError = (res, message, statusCode = 400) => {
  return sendResponse(res, statusCode, false, message);
};

const sendServerError = (res, message = 'Internal server error') => {
  return sendResponse(res, 500, false, message);
};

module.exports = {
  sendResponse,
  sendSuccess,
  sendError,
  sendServerError
};