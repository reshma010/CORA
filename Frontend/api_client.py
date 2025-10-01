# Oleg Korobeyko
import requests
import json
from typing import Dict, Any, Optional, Tuple

class APIClient:
    """
    HTTP client for communicating with the CORA backend API
    """
    
    def __init__(self, base_url: str = "https://corabackend.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def set_auth_token(self, token: str):
        """Set the JWT token for authenticated requests"""
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        
    def clear_auth_token(self):
        """Clear the JWT token"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def register(self, first_name: str, last_name: str, email: str, password: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Register a new user
        
        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email (must be @wayne.edu)
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            # Validate wayne.edu email on frontend as well
            if not email.endswith("@wayne.edu"):
                return False, "Only @wayne.edu email addresses are allowed.", {}
                
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "password": password
                },
                headers={'Content-Type': 'application/json'},
                timeout=30  # 30 second timeout
            )
            
            data = response.json()
            
            if response.status_code == 201:
                # Store the token for authenticated requests
                if 'data' in data and 'token' in data['data']:
                    self.set_auth_token(data['data']['token'])
                return True, data.get('message', 'Registration successful! Please check your email for verification.'), data.get('data', {})
            elif response.status_code == 500:
                # Check if it's an email service error
                error_msg = data.get('message', '').lower()
                if 'timeout' in error_msg or 'etimedout' in error_msg or 'smtp' in error_msg:
                    return False, "Registration completed but verification email could not be sent due to email service issues. You can try resending the verification email later.", {}
                else:
                    return False, data.get('message', 'Registration failed due to server error'), {}
            else:
                return False, data.get('message', 'Registration failed'), {}
                
        except requests.exceptions.Timeout:
            return False, "Registration request timed out. Please try again.", {}
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Please check your internet connection.", {}
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError:
            return False, "Invalid response from server", {}
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Login user
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            print(f" API: Starting login request for {email}")
            
            # Validate wayne.edu email on frontend as well
            if not email.endswith("@wayne.edu"):
                print(" API: Email validation failed - not @wayne.edu")
                return False, "Only @wayne.edu email addresses are allowed.", {}
            
            print(f" API: Making POST request to {self.base_url}/api/auth/login")
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                headers={'Content-Type': 'application/json'},
                timeout=30  # Add timeout to prevent hanging
            )
            
            print(f" API: Response received - Status: {response.status_code}")
            
            data = response.json()
            print(f" API: Response data: {data}")
            
            if response.status_code == 200:
                print(" API: Login successful")
                # Store the token for authenticated requests
                if 'data' in data and 'token' in data['data']:
                    print(" API: Setting auth token")
                    self.set_auth_token(data['data']['token'])
                return True, data.get('message', 'Login successful'), data.get('data', {})
            else:
                print(f" API: Login failed with status {response.status_code}")
                return False, data.get('message', 'Login failed'), {}
                
        except requests.exceptions.ConnectionError as e:
            print(f" API: Connection error: {str(e)}")
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.Timeout as e:
            print(f" API: Timeout error: {str(e)}")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError as e:
            print(f" API: JSON decode error: {str(e)}")
            return False, "Invalid response from server", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Unexpected error: {str(e)}", {}
    
    def get_user_profile(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get current user profile (requires authentication)
        
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            if not self.token:
                return False, "Not authenticated", {}
                
            response = self.session.get(
                f"{self.base_url}/api/auth/me",
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return True, "Profile retrieved successfully", data.get('data', {})
            else:
                return False, data.get('message', 'Failed to get profile'), {}
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError:
            return False, "Invalid response from server", {}
    
    def resend_verification_email(self, email: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Resend email verification
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/resend-verification",
                json={"email": email},
                headers={'Content-Type': 'application/json'},
                timeout=30  # 30 second timeout
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return True, data.get('message', 'Verification email sent successfully!'), data.get('data', {})
            elif response.status_code == 500:
                # Check if it's an email service error
                error_msg = data.get('message', '').lower()
                if 'timeout' in error_msg or 'etimedout' in error_msg or 'smtp' in error_msg:
                    return False, "Email service temporarily unavailable. The server is experiencing issues with the email provider. Please try again later or contact support.", {}
                else:
                    return False, data.get('message', 'Server error occurred while sending email'), {}
            else:
                return False, data.get('message', 'Failed to send verification email'), {}
                
        except requests.exceptions.Timeout:
            return False, "Request timed out. The email service may be experiencing issues. Please try again later.", {}
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Please check your internet connection and try again.", {}
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError:
            return False, "Invalid response from server. Please try again.", {}
    
    def get_robots(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get all robots with detection statistics (requires authentication)
        
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            if not self.token:
                return False, "Not authenticated", {}
                
            print(" API: Getting robots with detection data...")
                
            response = self.session.get(
                f"{self.base_url}/api/robots",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200:
                robots_data = data.get('data', {})
                robots_list = robots_data.get('robots', [])
                print(f" API: Found {len(robots_list)} robots")
                
                # Transform data to match frontend expectations
                formatted_data = {
                    'units': robots_list,  # Frontend expects 'units' key
                    'units_count': len(robots_list),
                    'robots': robots_list  # Keep original for compatibility
                }
                
                return True, "Robots retrieved successfully", formatted_data
            else:
                return False, data.get('message', 'Failed to get robots'), {}
                
        except requests.exceptions.ConnectionError:
            print(" API: Cannot connect to server")
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError:
            print(" API: Invalid JSON response")
            return False, "Invalid response from server", {}
    
    def check_verification_status(self, email: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if user's email is verified
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (success, message, data)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/check-verification",
                json={'email': email},
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return True, "Verification status retrieved", data.get('data', {})
            else:
                return False, data.get('message', 'Failed to check verification status'), {}
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError:
            return False, "Invalid response from server", {}

    def send_password_reset(self, email: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Send password reset email
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            print(f" API: Sending password reset request for {email}")
            print(f" API: URL: {self.base_url}/api/auth/forgot-password")
            print(f" API: Payload: {{'email': '{email}'}}")
            
            response = self.session.post(
                f"{self.base_url}/api/auth/forgot-password",
                json={'email': email},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f" API: Password reset response - Status: {response.status_code}")
            
            data = response.json()
            print(f" API: Password reset data: {data}")
            
            if response.status_code == 200:
                print(" API: Password reset email sent successfully")
                return True, data.get('message', 'Password reset email sent'), data.get('data', {})
            else:
                print(f" API: Password reset failed with status {response.status_code}")
                return False, data.get('message', 'Failed to send password reset email'), {}
                
        except requests.exceptions.ConnectionError as e:
            print(f" API: Connection error: {str(e)}")
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.Timeout as e:
            print(f" API: Timeout error: {str(e)}")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError as e:
            print(f" API: JSON decode error: {str(e)}")
            return False, "Invalid response from server", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Unexpected error: {str(e)}", {}

    def reset_password_with_token(self, token: str, new_password: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Reset password using reset token
        
        Args:
            token: The password reset token from email
            new_password: The new password
            
        Returns:
            Tuple of (success, message, data)
        """
        try:
            endpoint = f"{self.base_url}/api/auth/reset-password"
            payload = {
                'token': token,
                'password': new_password
            }
            
            print(f" API: Resetting password with token")
            response = requests.post(
                endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            print(f" API: Password reset response - Status: {response.status_code}")
            data = response.json()
            print(f" API: Password reset data: {data}")
            
            if response.status_code == 200:
                print(" API: Password reset successful")
                return True, data.get('message', 'Password reset successful'), data.get('data', {})
            else:
                print(f" API: Password reset failed with status {response.status_code}")
                return False, data.get('message', 'Failed to reset password'), {}
                
        except requests.exceptions.ConnectionError as e:
            print(f" API: Connection error: {str(e)}")
            return False, "Cannot connect to server. Please ensure the backend is running.", {}
        except requests.exceptions.Timeout as e:
            print(f" API: Timeout error: {str(e)}")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except json.JSONDecodeError as e:
            print(f" API: JSON decode error: {str(e)}")
            return False, "Invalid response from server", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Unexpected error: {str(e)}", {}

    def get_active_units(self, hours: int = 24) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get list of active robot units
        
        Args:
            hours: Time range to consider "active" (default: 24)
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            print(f" API: Getting active units (last {hours} hours)")
            
            response = self.session.get(
                f"{self.base_url}/api/detections/active",
                params={'hours': hours},
                timeout=10
            )
            
            print(f" API: Response received - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f" API: Found {data.get('data', {}).get('units_count', 0)} active units")
                return True, data.get('message', 'Success'), data.get('data', {})
            else:
                data = response.json()
                error_msg = data.get('message', f'HTTP {response.status_code}')
                print(f" API: Failed to get active units - {error_msg}")
                return False, error_msg, {}
                
        except requests.exceptions.Timeout:
            print(" API: Request timed out")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            return False, f"Unexpected error: {str(e)}", {}

    def get_unit_detections(self, unit_id: str, hours: int = 24, limit: int = 100, action_type: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get detection data for a specific robot unit
        
        Args:
            unit_id: Robot unit identifier
            hours: Time range in hours (default: 24)
            limit: Maximum number of packages to return (default: 100)
            action_type: Filter by specific action type (optional)
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            print(f" API: Getting detections for unit {unit_id}")
            
            params = {'hours': hours, 'limit': limit}
            if action_type:
                params['action_type'] = action_type
            
            response = self.session.get(
                f"{self.base_url}/api/detections/{unit_id}",
                params=params,
                timeout=15
            )
            
            print(f" API: Response received - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_detections = data.get('data', {}).get('total_detections', 0)
                print(f" API: Found {total_detections} detections for unit {unit_id}")
                return True, data.get('message', 'Success'), data.get('data', {})
            else:
                data = response.json()
                error_msg = data.get('message', f'HTTP {response.status_code}')
                print(f" API: Failed to get unit detections - {error_msg}")
                return False, error_msg, {}
                
        except requests.exceptions.Timeout:
            print(" API: Request timed out")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            return False, f"Unexpected error: {str(e)}", {}

    def get_unit_summary(self, unit_id: str, hours: int = 24) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get detection summary statistics for a robot unit
        
        Args:
            unit_id: Robot unit identifier
            hours: Time range in hours (default: 24)
            
        Returns:
            Tuple of (success: bool, message: str, data: dict)
        """
        try:
            print(f" API: Getting summary for unit {unit_id}")
            
            response = self.session.get(
                f"{self.base_url}/api/detections/{unit_id}/summary",
                params={'hours': hours},
                timeout=10
            )
            
            print(f" API: Response received - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f" API: Got summary for unit {unit_id}")
                return True, data.get('message', 'Success'), data.get('data', {})
            else:
                data = response.json()
                error_msg = data.get('message', f'HTTP {response.status_code}')
                print(f" API: Failed to get unit summary - {error_msg}")
                return False, error_msg, {}
                
        except requests.exceptions.Timeout:
            print(" API: Request timed out")
            return False, "Request timed out. Please try again.", {}
        except requests.exceptions.RequestException as e:
            print(f" API: Request exception: {str(e)}")
            return False, f"Network error: {str(e)}", {}
        except Exception as e:
            print(f" API: Unexpected error: {type(e).__name__}: {str(e)}")
            return False, f"Unexpected error: {str(e)}", {}

# Global API client instance
api_client = APIClient()