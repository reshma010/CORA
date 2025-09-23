const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const { validationResult } = require('express-validator');
const User = require('../models/User');
const { sendSuccess, sendError, sendServerError } = require('../utils/response');
const emailService = require('../utils/emailService');

// Generate JWT token
const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRE || '7d'
  });
};

// @desc    Register user
// @route   POST /api/auth/register
// @access  Public
const register = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, errors.array()[0].msg, 400);
    }

    const { name, email, password } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      // If user exists but is not verified, allow re-registration
      if (!existingUser.isEmailVerified) {
        // Delete the old unverified user and create a new one
        await User.deleteOne({ email });
        console.log(`Deleted previous unverified user for email: ${email}`);
        
        // Wait a moment to ensure database consistency
        await new Promise(resolve => setTimeout(resolve, 100));
      } else {
        return sendError(res, 'User already exists', 400);
      }
    }

    // Create user with explicit false for email verification
    const userData = {
      name,
      email,
      password,
      isEmailVerified: false,  // CRITICAL: Must be false
      emailVerificationToken: undefined,
      emailVerificationExpires: undefined,
      isActive: true,
      role: 'user'
    };
    
    console.log(`Creating user with data:`, { 
      email: userData.email, 
      isEmailVerified: userData.isEmailVerified 
    });
    
    const user = await User.create(userData);
    
    console.log(`Created new user: ${email}, isEmailVerified: ${user.isEmailVerified}, _id: ${user._id}`);

    // Generate email verification token
    const verificationToken = user.generateEmailVerificationToken();
    await user.save();
    
    console.log(`After token generation - User: ${email}, isEmailVerified: ${user.isEmailVerified}, hasToken: ${!!user.emailVerificationToken}`);
    
    // Double-check the user is not verified
    if (user.isEmailVerified === true) {
      console.log(`CRITICAL ERROR: User was auto-verified during creation! This is NOT expected!`);
    }

    // Send verification email
    try {
      await emailService.sendEmailVerification(email, name, verificationToken);
      console.log(`Verification email sent to ${email}`);
    } catch (error) {
      console.error('Failed to send verification email:', error);
      // Continue with registration even if email fails
    }

    // Generate JWT token for immediate login
    const token = generateToken(user._id);

    sendSuccess(res, 'User registered successfully. Please check email to verify account.', {
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        isEmailVerified: user.isEmailVerified
      }
    }, 201);

  } catch (error) {
    console.error('Register error:', error);
    sendServerError(res, 'Error registering user');
  }
};

// @desc    Login user
// @route   POST /api/auth/login
// @access  Public
const login = async (req, res) => {
  try {
    console.log('LOGIN API: Request received');
    console.log('LOGIN API: Request body:', { email: req.body.email, password: '[HIDDEN]' });
    console.log('LOGIN API: Environment check - NODE_ENV:', process.env.NODE_ENV);
    console.log('LOGIN API: JWT_SECRET exists:', !!process.env.JWT_SECRET);

    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      console.log('LOGIN API: Validation errors:', errors.array());
      return sendError(res, errors.array()[0].msg, 400);
    }

    const { email, password } = req.body;
    console.log(`LOGIN API: Looking for user with email: ${email}`);

    // Check for user
    const user = await User.findOne({ email }).select('+password');
    
    if (!user) {
      console.log('LOGIN API: User not found');
      return sendError(res, 'Invalid credentials', 401);
    }

    console.log(`LOGIN API: User found: ${user.email}, ID: ${user._id}`);
    console.log('LOGIN API: Stored password hash:', user.password ? user.password.substring(0, 20) + '...' : 'undefined');
    console.log('LOGIN API: Input password length:', password ? password.length : 0);
    
    console.log('LOGIN API: About to check password match...');
    const passwordMatch = await user.matchPassword(password);
    console.log(`LOGIN API: Password match result: ${passwordMatch}`);
    
    if (!passwordMatch) {
      console.log('LOGIN API: Password mismatch - entered password does not match stored hash');
      return sendError(res, 'Invalid credentials', 401);
    }

    console.log('LOGIN API: Checking if user is active...');
    if (!user.isActive) {
      console.log('LOGIN API: Account is deactivated');
      return sendError(res, 'Account is deactivated', 401);
    }

    console.log('LOGIN API: Updating last login time...');
    // Update last login
    user.lastLogin = new Date();
    await user.save();

    console.log('LOGIN API: Checking JWT_SECRET environment variable...');
    if (!process.env.JWT_SECRET) {
      console.error('LOGIN API: JWT_SECRET environment variable is missing!');
      throw new Error('JWT_SECRET not configured');
    }

    console.log('LOGIN API: Generating JWT token...');
    // Generate token
    const token = generateToken(user._id);

    console.log('LOGIN API: Login successful, sending response');
    sendSuccess(res, 'Login successful', {
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        lastLogin: user.lastLogin
      }
    });
    console.log('LOGIN API: Response sent successfully');

  } catch (error) {
    console.error('LOGIN API: Error occurred:', error);
    console.error('LOGIN API: Error stack:', error.stack);
    console.error('LOGIN API: Error name:', error.name);
    console.error('LOGIN API: Error message:', error.message);
    sendServerError(res, 'Error logging in');
  }
};

// @desc    Get current user
// @route   GET /api/auth/me
// @access  Private
const getMe = async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    sendSuccess(res, 'User profile retrieved', {
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        isActive: user.isActive,
        createdAt: user.createdAt,
        lastLogin: user.lastLogin
      }
    });

  } catch (error) {
    console.error('Get user error:', error);
    sendServerError(res, 'Error getting user profile');
  }
};

// @desc    Verify email
// @route   GET /api/auth/verify-email/:token
// @access  Public
const verifyEmail = async (req, res) => {
  try {
    const { token } = req.params;
    
    // STRICT CHECK: Token must be provided and valid
    if (!token || token.length < 32) {
      console.log(`INVALID VERIFICATION ATTEMPT: Token length ${token ? token.length : 0}, token: ${token}`);
      return sendError(res, 'Invalid verification token', 400);
    }
    
    // Check for email client prefetching/bot activity
    const userAgent = req.get('User-Agent') || '';
    const isBot = /bot|crawler|spider|crawling|prefetch|preview|scanner|LinkPreview|WhatsApp|Slack|Discord|Teams|SkypeUriPreview/i.test(userAgent);
    
    if (isBot) {
      console.log(`EMAIL CLIENT PREFETCH DETECTED: ${userAgent} - Blocking auto-verification`);
      return res.status(200).send(`
        <!DOCTYPE html>
        <html><head><title>Email Link Detected - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Email Link Scanned</h1>
          <p>This verification link was accessed by an email client security scanner.</p>
          <p>Please click the link from the email client to verify the account.</p>
        </body></html>
      `);
    }
    
    console.log(`EMAIL VERIFICATION LINK CLICKED! Token: ${token.substring(0, 8)}... (length: ${token.length}) User-Agent: ${userAgent}`);

    // Hash the token to match what's stored in database
    const hashedToken = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    // Find user with matching token that hasn't expired
    const user = await User.findOne({
      emailVerificationToken: hashedToken,
      emailVerificationExpires: { $gt: Date.now() }
    });

    if (!user) {
      console.log(`NO USER FOUND for token: ${token.substring(0, 8)}...`);
      return sendError(res, 'Invalid or expired verification token', 400);
    }

    console.log(`Found user to verify: ${user.email}`);

    // CRITICAL: Only verify if there is a valid token and user
    console.log(`SHOWING VERIFICATION PAGE FOR: ${user.email}`);

    // STRICT VERIFICATION: Double-check user is not already verified
    if (user.isEmailVerified) {
      console.log(`User ${user.email} is already verified!`);
      return res.status(200).send(`
        <!DOCTYPE html>
        <html><head><title>Already Verified - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Email Already Verified</h1>
          <p>Email ${user.email} is already verified.</p>
        </body></html>
      `);
    }
    
    // DON'T VERIFY YET - Show confirmation page that requires user click

    // Return confirmation page that requires user to enter their email
    res.status(200).send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Verify Email - CORA</title>
        <style>
          body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background-color: #f3f7f6;
          }
          .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          }
          .logo { color: #0c554a; font-size: 32px; font-weight: bold; margin-bottom: 30px; }
          .message { color: #0f1614; font-size: 16px; line-height: 1.5; margin-bottom: 30px; }
          .input {
            width: 80%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #b2a48f;
            border-radius: 10px;
            margin: 10px 0;
            box-sizing: border-box;
          }
          .input:focus {
            border-color: #0c554a;
            outline: none;
          }
          .button {
            background-color: #0c554a;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 25px;
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
            border: none;
            cursor: pointer;
            margin-top: 20px;
          }
          .button:hover { background-color: #0a4a40; }
          .button:disabled { 
            background-color: #ccc; 
            cursor: not-allowed;
          }
          .warning { 
            background-color: #edbc2c; 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0; 
            color: #0f1614;
            font-weight: bold;
          }
          .error {
            color: #d32f2f;
            font-size: 14px;
            margin-top: 10px;
            display: none;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="logo">CORA</div>
          <div class="message">
            <h2>Verify Email Address</h2>
            <p>To confirm this verification request is legitimate, please enter the email address below:</p>
          </div>
          <form id="verificationForm" method="POST" action="/api/auth/confirm-verification/${token}">
            <input type="hidden" name="token" value="${token}">
            <input type="email" 
                   class="input" 
                   id="emailInput" 
                   name="email" 
                   placeholder="Enter email address" 
                   required 
                   autocomplete="email">
            <div class="error" id="errorMessage">Please enter a valid email address</div>
            <div class="warning">
              Only enter email if attempting to verify CORA account
            </div>
            <button type="submit" class="button" id="verifyButton">Verify Email</button>
          </form>
        </div>
        
        <script>
          document.getElementById('verificationForm').addEventListener('submit', function(e) {
            const email = document.getElementById('emailInput').value.trim();
            const errorMsg = document.getElementById('errorMessage');
            
            if (!email || !email.includes('@')) {
              e.preventDefault();
              errorMsg.style.display = 'block';
              errorMsg.textContent = 'Please enter a valid email address';
              return;
            }
            
            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
              e.preventDefault();
              errorMsg.style.display = 'block';
              errorMsg.textContent = 'Please enter a valid email address';
              return;
            }
            
            errorMsg.style.display = 'none';
            document.getElementById('verifyButton').textContent = 'Verifying...';
            document.getElementById('verifyButton').disabled = true;
          });
        </script>
      </body>
      </html>
    `);

  } catch (error) {
    console.error('Email verification error:', error);
    sendServerError(res, 'Error verifying email');
  }
};

// @desc    Resend email verification
// @route   POST /api/auth/resend-verification
// @access  Public
const resendVerification = async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return sendError(res, 'Email is required', 400);
    }

    const user = await User.findOne({ email });
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    if (user.isEmailVerified) {
      return sendError(res, 'Email is already verified', 400);
    }

    // Generate new verification token
    const verificationToken = user.generateEmailVerificationToken();
    await user.save();

    // Send verification email
    try {
      await emailService.sendEmailVerification(email, user.name, verificationToken);
      sendSuccess(res, 'Verification email sent successfully');
    } catch (error) {
      console.error('Failed to send verification email:', error);
      sendServerError(res, 'Failed to send verification email');
    }

  } catch (error) {
    console.error('Resend verification error:', error);
    sendServerError(res, 'Error resending verification email');
  }
};

// @desc    Check email verification status
// @route   POST /api/auth/check-verification
// @access  Public
const checkVerificationStatus = async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return sendError(res, 'Email is required', 400);
    }

    const user = await User.findOne({ email }).select('isEmailVerified createdAt');
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    console.log(`Verification status check for ${email}: isEmailVerified=${user.isEmailVerified}, created=${user.createdAt}`);
    
    // CRITICAL CHECK: If user is verified but no verification was logged, something's wrong
    if (user.isEmailVerified && !user.emailVerificationToken) {
      console.log(`User ${email} is verified but has no verification token - this means verification happened!`);
    } else if (user.isEmailVerified && user.emailVerificationToken) {
      console.log(`CRITICAL: User ${email} is verified but STILL HAS verification token - this is NOT expected!`);
    }

    sendSuccess(res, 'Verification status retrieved', {
      isEmailVerified: user.isEmailVerified
    });

  } catch (error) {
    console.error('Check verification status error:', error);
    sendServerError(res, 'Error checking verification status');
  }
};

// @desc    Confirm email verification (two-step process)
// @route   POST /api/auth/confirm-verification/:token
// @access  Public
const confirmEmailVerification = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).send(`
        <!DOCTYPE html>
        <html><head><title>Invalid Email - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Invalid Email Address</h1>
          <p>${errors.array()[0].msg}</p>
          <a href="/api/auth/verify-email/${req.params.token}" style="color: #0c554a;">Try Again</a>
        </body></html>
      `);
    }

    const { token: paramToken } = req.params;
    const { email, token: bodyToken } = req.body;
    const token = paramToken || bodyToken;
    
    if (!token || token.length < 32) {
      console.log(`INVALID VERIFICATION ATTEMPT: Token length ${token ? token.length : 0}, token: ${token}`);
      return res.status(400).send(`
        <!DOCTYPE html>
        <html><head><title>Invalid Token - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Invalid Verification Token</h1>
          <p>The verification token is invalid or has expired.</p>
          <p>Please request a new verification email.</p>
        </body></html>
      `);
    }
    
    if (!email) {
      return res.status(400).send(`
        <!DOCTYPE html>
        <html><head><title>Email Required - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Email Address Required</h1>
          <p>Please provide email address to verify.</p>
          <a href="/api/auth/verify-email/${token}" style="color: #0c554a;">Try Again</a>
        </body></html>
      `);
    }
    
    console.log(`USER CONFIRMED EMAIL VERIFICATION! Token: ${token.substring(0, 8)}... (length: ${token.length}) Email: ${email}`);

    // Hash the token to match what's stored in database
    const hashedToken = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    // Find user with matching token that hasn't expired
    const user = await User.findOne({
      emailVerificationToken: hashedToken,
      emailVerificationExpires: { $gt: Date.now() }
    });

    if (!user) {
      console.log(`NO USER FOUND for token: ${token.substring(0, 8)}...`);
      return res.status(400).send('<h1>Invalid or expired verification token</h1>');
    }

    // Verify the email matches the user
    if (user.email.toLowerCase() !== email.toLowerCase()) {
      console.log(`EMAIL MISMATCH: Expected ${user.email}, got ${email}`);
      return res.status(400).send(`
        <!DOCTYPE html>
        <html><head><title>Email Mismatch - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Email Address Mismatch</h1>
          <p>The email address entered does not match the verification token.</p>
          <a href="/api/auth/verify-email/${token}" style="color: #0c554a;">Try Again</a>
        </body></html>
      `);
    }

    if (user.isEmailVerified) {
      console.log(`User ${user.email} is already verified!`);
      return res.status(200).send(`
        <!DOCTYPE html>
        <html><head><title>Already Verified - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
          <h1>Email Already Verified</h1>
          <p>Email ${user.email} is already verified.</p>
        </body></html>
      `);
    }

    // ACTUALLY VERIFY THE EMAIL HERE
    user.isEmailVerified = true;
    user.emailVerificationToken = undefined;
    user.emailVerificationExpires = undefined;
    await user.save();
    
    console.log(`EMAIL VERIFIED: ${user.email} - isEmailVerified now: ${user.isEmailVerified}`);

    // Send welcome email with delay to ensure it comes after verification
    try {
      setTimeout(async () => {
        try {
          await emailService.sendWelcomeEmail(user.email, user.name);
          console.log(`Welcome email sent to ${user.email}`);
        } catch (error) {
          console.error('Failed to send welcome email:', error);
        }
      }, 5000); // Increased delay to 5 seconds
    } catch (error) {
      console.error('Failed to schedule welcome email:', error);
    }

    // Return success page
    res.status(200).send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Email Verified - CORA</title>
        <style>
          body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f3f7f6; }
          .container { max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
          .success { color: #0c554a; font-size: 24px; margin-bottom: 20px; }
          .message { color: #0f1614; font-size: 16px; line-height: 1.5; }
          .logo { color: #0c554a; font-size: 32px; font-weight: bold; margin-bottom: 30px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="logo">CORA</div>
          <div class="success">Email Verified Successfully!</div>
          <div class="message">
            <p>Hello ${user.name},</p>
            <p>Email address <strong>${user.email}</strong> has been verified successfully.</p>
            <p>Close this window and return to the CORA application to continue.</p>
          </div>
        </div>
      </body>
      </html>
    `);

  } catch (error) {
    console.error('Email verification error:', error);
    res.status(500).send('<h1>Error verifying email</h1>');
  }
};

// @desc    Forgot password
// @route   POST /api/auth/forgot-password
// @access  Public
const forgotPassword = async (req, res) => {
  try {
    console.log('FORGOT PASSWORD: Request received');
    
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      console.log('FORGOT PASSWORD: Validation errors:', errors.array());
      return sendError(res, errors.array()[0].msg, 400);
    }

    const { email } = req.body;
    console.log(`FORGOT PASSWORD: Looking for user with email: ${email}`);

    const user = await User.findOne({ email });
    
    if (!user) {
      console.log('FORGOT PASSWORD: User not found');
      // For security, always return success even if user doesn't exist
      return sendSuccess(res, 'If email is registered, reset instructions will be sent shortly.');
    }

    console.log(`FORGOT PASSWORD: User found: ${user.email}`);

    // Generate password reset token
    const resetToken = user.generatePasswordResetToken();
    await user.save();

    console.log('FORGOT PASSWORD: Reset token generated, sending email');

    // Send reset email
    try {
      await emailService.sendPasswordResetEmail(email, user.name, resetToken);
      console.log(`FORGOT PASSWORD: Reset email sent to ${email}`);
    } catch (error) {
      console.error('FORGOT PASSWORD: Failed to send email:', error);
      // Clear the reset token if email fails
      user.passwordResetToken = undefined;
      user.passwordResetExpires = undefined;
      await user.save();
      return sendServerError(res, 'Failed to send reset email');
    }

    sendSuccess(res, 'If email is registered, reset instructions will be sent shortly.');

  } catch (error) {
    console.error('FORGOT PASSWORD: Error occurred:', error);
    sendServerError(res, 'Error processing password reset request');
  }
};

// @desc    Reset password
// @route   POST /api/auth/reset-password/:token
// @access  Public
const resetPassword = async (req, res) => {
  try {
    console.log('RESET PASSWORD: Request received');
    
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      console.log('RESET PASSWORD: Validation errors:', errors.array());
      return sendError(res, errors.array()[0].msg, 400);
    }

    const { token } = req.params;
    const { password } = req.body;

    console.log(`RESET PASSWORD: Processing token: ${token.substring(0, 8)}...`);

    // Hash the token to match what's stored in database
    const hashedToken = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    // Find user with matching token that hasn't expired
    const user = await User.findOne({
      passwordResetToken: hashedToken,
      passwordResetExpires: { $gt: Date.now() }
    });

    if (!user) {
      console.log('RESET PASSWORD: Invalid or expired token');
      return sendError(res, 'Invalid or expired reset token', 400);
    }

    console.log(`RESET PASSWORD: Valid token for user: ${user.email}`);
    console.log('RESET PASSWORD: Old password hash:', user.password ? user.password.substring(0, 20) + '...' : 'undefined');

    // Set new password
    user.password = password;
    user.passwordResetToken = undefined;
    user.passwordResetExpires = undefined;
    
    console.log('RESET PASSWORD: About to save user with new password');
    await user.save();
    
    // Fetch user again to verify password was saved correctly
    const updatedUser = await User.findById(user._id).select('+password');
    console.log('RESET PASSWORD: New password hash:', updatedUser.password ? updatedUser.password.substring(0, 20) + '...' : 'undefined');
    console.log('RESET PASSWORD: Password updated successfully');

    sendSuccess(res, 'Password has been reset successfully. Login with the new password.');

  } catch (error) {
    console.error('RESET PASSWORD: Error occurred:', error);
    sendServerError(res, 'Error resetting password');
  }
};

// @desc    Show password reset form
// @route   GET /api/auth/reset-password/:token
// @access  Public
const showResetPasswordForm = async (req, res) => {
  try {
    const { token } = req.params;
    
    console.log(`SHOW RESET FORM: Token: ${token.substring(0, 8)}...`);

    // Validate token first
    const hashedToken = crypto
      .createHash('sha256')
      .update(token)
      .digest('hex');

    const user = await User.findOne({
      passwordResetToken: hashedToken,
      passwordResetExpires: { $gt: Date.now() }
    });

    if (!user) {
      console.log('SHOW RESET FORM: Invalid or expired token');
      return res.status(400).send(`
        <!DOCTYPE html>
        <html><head><title>Invalid Reset Link - CORA</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background-color: #f3f7f6;">
          <h1 style="color: #d32f2f;">Invalid or Expired Reset Link</h1>
          <p>This password reset link is invalid or has expired.</p>
          <p>Please request a new password reset from the login page.</p>
        </body></html>
      `);
    }

    console.log(`SHOW RESET FORM: Valid token for user: ${user.email}`);

    // Show password reset form with external CSS and JS
    res.status(200).send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Reset Password - CORA</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="/css/reset-password.css">
      </head>
      <body>
        <div class="container">
          <div class="logo">CORA</div>
          <div class="message">
            <h2>Reset Password</h2>
            <p>Enter new password below:</p>
          </div>
          <form id="resetForm" method="POST" action="/api/auth/reset-password/${token}">
            <div class="password-container">
              <input type="password" 
                     class="input" 
                     id="passwordInput"
                     name="password" 
                     placeholder="Enter new password" 
                     required 
                     minlength="10"
                     maxlength="20">
              <button type="button" 
                      id="togglePassword" 
                      class="toggle-password"
                      title="Show/Hide Password">
                &#128065;
              </button>
              <div class="char-counter" id="charCounter">0/20</div>
            </div>
            
            <div class="password-container">
              <input type="password" 
                     class="input" 
                     id="confirmPasswordInput"
                     name="confirmPassword" 
                     placeholder="Confirm new password" 
                     required 
                     minlength="10"
                     maxlength="20">
              <button type="button" 
                      id="toggleConfirmPassword" 
                      class="toggle-password"
                      title="Show/Hide Password">
                &#128065;
              </button>
            </div>
            
            <div class="error" id="errorMessage"></div>
            
            <div class="requirements">
              <strong>Password Requirements:</strong>
              <div class="req-item req-pending" id="req-length">10-20 characters long</div>
              <div class="req-item req-pending" id="req-upper">At least one uppercase letter</div>
              <div class="req-item req-pending" id="req-lower">At least one lowercase letter</div>
              <div class="req-item req-pending" id="req-number">At least one number</div>
              <div class="req-item req-pending" id="req-special">At least one special character (!@#$%^&*(),.?":{}|<>)</div>
              <div class="req-item req-pending" id="req-match">Passwords must match</div>
            </div>
            
            <button type="submit" class="button" id="submitBtn" disabled>Reset Password</button>
          </form>
        </div>
        
        <script src="/js/reset-password.js"></script>
      </body>
      </html>
    `);

  } catch (error) {
    console.error('SHOW RESET FORM: Error occurred:', error);
    res.status(500).send('<h1>Error loading reset form</h1>');
  }
};

module.exports = {
  register,
  login,
  getMe,
  verifyEmail,
  resendVerification,
  checkVerificationStatus,
  confirmEmailVerification,
  forgotPassword,
  resetPassword,
  showResetPasswordForm
};