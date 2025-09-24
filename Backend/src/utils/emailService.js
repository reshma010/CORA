//Oleg Korobeyko
const sgMail = require('@sendgrid/mail');

class EmailService {
  constructor() {
    // Set SendGrid API key
    sgMail.setApiKey(process.env.SENDGRID_API_KEY);
    
    // Log configuration status
    if (process.env.SENDGRID_API_KEY) {
      console.log('SendGrid API key configured');
    } else {
      console.error('SENDGRID_API_KEY environment variable is missing');
    }
  }

  async sendEmailVerification(email, name, verificationToken) {
    const verificationUrl = `https://corabackend.onrender.com/api/auth/verify-email/${verificationToken}`;
    
    const mailOptions = {
      to: email,
      from: {
        email: process.env.EMAIL_FROM || process.env.EMAIL_USER || 'noreply@cora.com',
        name: 'CORA System'
      },
      subject: 'CORA - Verify Email Address',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background-color: #0c554a; color: white; padding: 20px; text-align: center;">
            <h1>CORA System</h1>
          </div>
          
          <div style="padding: 20px; background-color: #f3f7f6;">
            <h2 style="color: #0c554a;">Welcome to CORA, ${name}!</h2>
            
            <p>Thank you for registering with CORA. To complete account setup, please verify email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${verificationUrl}" 
                 style="background-color: #0c554a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email
              </a>
            </div>
            
            <p>Or copy and paste this link into the browser:</p>
            <p style="word-break: break-all; color: #666;">
              <a href="${verificationUrl}">${verificationUrl}</a>
            </p>
            
            <p><strong>This link expires in 24 hours.</strong></p>
            
            <p>If you didn't create an account with CORA, please ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #666; font-size: 14px;">
              This is an automated message from the CORA system. Please do not reply to this email.
            </p>
          </div>
        </div>
      `
    };

    try {
      const result = await sgMail.send(mailOptions);
      console.log(`VERIFICATION email sent to ${email} via SendGrid`);
      return { success: true, messageId: result[0].headers['x-message-id'] };
    } catch (error) {
      console.error('VERIFICATION email send error:', error.response?.body || error.message);
      return { success: false, error: error.message };
    }
  }

  async sendWelcomeEmail(email, name) {
    const mailOptions = {
      to: email,
      from: {
        email: process.env.EMAIL_FROM || process.env.EMAIL_USER || 'noreply@cora.com',
        name: 'CORA System'
      },
      subject: 'Welcome to CORA!',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background-color: #0c554a; color: white; padding: 20px; text-align: center;">
            <h1>CORA System</h1>
          </div>
          
          <div style="padding: 20px; background-color: #f3f7f6;">
            <h2 style="color: #0c554a;">Welcome to CORA, ${name}!</h2>
            
            <p>Email has been verified successfully. Access to all features of the CORA system is now available.</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}" 
                 style="background-color: #edbc2c; color: #0f1614; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Access CORA
              </a>
            </div>
            
            <p>If there are any questions or assistance is needed, please contact the support team.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #666; font-size: 14px;">
              This is an automated message from the CORA system.
            </p>
          </div>
        </div>
      `
    };

    try {
      const result = await sgMail.send(mailOptions);
      console.log(`WELCOME email sent to ${email} via SendGrid`);
      return { success: true, messageId: result[0].headers['x-message-id'] };
    } catch (error) {
      console.error('WELCOME email send error:', error.response?.body || error.message);
      return { success: false, error: error.message };
    }
  }

  async sendPasswordResetEmail(email, name, resetToken) {
    const resetUrl = `https://corabackend.onrender.com/api/auth/reset-password/${resetToken}`;
    
    const mailOptions = {
      to: email,
      from: {
        email: process.env.EMAIL_FROM || process.env.EMAIL_USER || 'noreply@cora.com',
        name: 'CORA System'
      },
      subject: 'CORA - Password Reset Request',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background-color: #0c554a; color: white; padding: 20px; text-align: center;">
            <h1>CORA System</h1>
          </div>
          
          <div style="padding: 20px; background-color: #f3f7f6;">
            <h2 style="color: #0c554a;">Password Reset Request</h2>
            
            <p>Hello ${name},</p>
            
            <p>A request to reset password for the CORA account was received. If this request was made, click the button below to reset password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${resetUrl}" 
                 style="background-color: #edbc2c; color: #0f1614; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Reset Password
              </a>
            </div>
            
            <p>Or copy and paste this link into the browser:</p>
            <p style="word-break: break-all; color: #666;">
              <a href="${resetUrl}">${resetUrl}</a>
            </p>
            
            <p><strong>This link expires in 1 hour.</strong></p>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #edbc2c; border-radius: 5px;">
              <p style="margin: 0; color: #0f1614;"><strong>Security Notice:</strong></p>
              <p style="margin: 5px 0 0 0; color: #0f1614; font-size: 14px;">
                If this password reset was not requested, please ignore this email. The password remains unchanged.
              </p>
            </div>
            
            <p style="color: #666; font-size: 14px; margin-top: 20px;">
              This is an automated message from the CORA system.
            </p>
          </div>
        </div>
      `
    };

    try {
      const result = await sgMail.send(mailOptions);
      console.log(`PASSWORD RESET email sent to ${email} via SendGrid`);
      return { success: true, messageId: result[0].headers['x-message-id'] };
    } catch (error) {
      console.error('PASSWORD RESET email send error:', error.response?.body || error.message);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new EmailService();