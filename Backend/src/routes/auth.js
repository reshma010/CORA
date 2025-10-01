const express = require('express');
const { body } = require('express-validator');
const { register, login, getMe, verifyEmail, resendVerification, checkVerificationStatus, confirmEmailVerification, forgotPassword, resetPassword, showResetPasswordForm } = require('../controllers/authController');
const auth = require('../middleware/auth');

const router = express.Router();

console.log(' AUTH ROUTES: Loading auth routes module...');
console.log(' AUTH ROUTES: forgotPassword function loaded:', typeof forgotPassword);
console.log(' AUTH ROUTES: resetPassword function loaded:', typeof resetPassword);

// Validation rules
const registerValidation = [
  body('firstName')
    .trim()
    .isLength({ min: 2, max: 25 })
    .withMessage('First name must be between 2 and 25 characters'),
  body('lastName')
    .trim()
    .isLength({ min: 2, max: 25 })
    .withMessage('Last name must be between 2 and 25 characters'),
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 10, max: 20 })
    .withMessage('Password must be between 10 and 20 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{10,20}$/)
    .withMessage('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*(),.?":{}|<>)')
];

const loginValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

// @route   POST /api/auth/register
// @desc    Register a new user
// @access  Public
router.post('/register', registerValidation, register);

// @route   POST /api/auth/login
// @desc    Login user
// @access  Public
router.post('/login', loginValidation, login);

// @route   GET /api/auth/me
// @desc    Get current user profile
// @access  Private
router.get('/me', auth, getMe);

// @route   GET /api/auth/verify-email/:token
// @desc    Verify email address
// @access  Public
router.get('/verify-email/:token', verifyEmail);

// @route   POST /api/auth/resend-verification
// @desc    Resend email verification
// @access  Public
router.post('/resend-verification', [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email')
], resendVerification);

// @route   POST /api/auth/check-verification
// @desc    Check email verification status
// @access  Public
router.post('/check-verification', [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email')
], checkVerificationStatus);

// @route   POST /api/auth/confirm-verification/:token
// @desc    Confirm email verification (requires user email input)
// @access  Public
router.post('/confirm-verification/:token', [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email')
], confirmEmailVerification);

// @route   POST /api/auth/forgot-password
// @desc    Send password reset email
// @access  Public
router.post('/forgot-password', [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email')
], (req, res, next) => {
  console.log(' ROUTE HIT: /api/auth/forgot-password');
  next();
}, forgotPassword);

// @route   GET /api/auth/reset-password/:token
// @desc    Show password reset form
// @access  Public
router.get('/reset-password/:token', (req, res, next) => {
  console.log(' ROUTE HIT: GET /api/auth/reset-password/:token');
  next();
}, showResetPasswordForm);

// @route   POST /api/auth/reset-password/:token
// @desc    Reset password with token
// @access  Public
router.post('/reset-password/:token', [
  body('password')
    .isLength({ min: 10, max: 20 })
    .withMessage('Password must be between 10 and 20 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{10,20}$/)
    .withMessage('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character (!@#$%^&*(),.?":{}|<>)')
], resetPassword);

module.exports = router;