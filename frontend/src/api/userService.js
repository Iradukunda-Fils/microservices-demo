/**
 * UserService API Module
 * 
 * Educational Note: This module handles all communication with the UserService backend.
 * 
 * UserService Responsibilities:
 * - User registration and authentication
 * - JWT token generation (RS256 with RSA keys)
 * - Two-factor authentication (TOTP)
 * - User profile management
 * 
 * Why separate API modules?
 * In a microservices architecture, each service has distinct responsibilities.
 * Organizing API calls by service makes it clear which backend service handles what,
 * and helps developers understand service boundaries.
 * 
 * Service Boundary: UserService manages everything related to user identity and authentication.
 */

import axiosInstance from '../utils/axios'

/**
 * Register a new user.
 * 
 * @param {Object} userData - User registration data
 * @param {string} userData.username - Username (unique)
 * @param {string} userData.email - Email address
 * @param {string} userData.password - Password
 * @returns {Promise<Object>} Registration response with user data
 * 
 * Educational Note: This calls UserService's registration endpoint.
 * The password is hashed on the backend using Django's PBKDF2 algorithm.
 */
export async function registerUser(userData) {
  const response = await axiosInstance.post('/api/users/register/', userData)
  return response.data
}

/**
 * Login user and get JWT tokens.
 * 
 * @param {Object} credentials - Login credentials
 * @param {string} credentials.username - Username
 * @param {string} credentials.password - Password
 * @returns {Promise<Object>} Login response with access token, refresh token, and user data
 * 
 * Educational Note: This calls UserService's token endpoint.
 * UserService generates JWT tokens signed with RSA private key (RS256).
 * Other services can verify these tokens using the public key without calling UserService.
 * This is more secure and scalable than symmetric signing (HS256).
 */
export async function loginUser(credentials) {
  const response = await axiosInstance.post('/api/token/', credentials)
  return response.data
}

/**
 * Get current user profile.
 * 
 * @returns {Promise<Object>} User profile data
 * 
 * Educational Note: This requires a valid JWT token in the Authorization header.
 * The axios interceptor automatically adds the token from localStorage.
 */
export async function getCurrentUser() {
  const response = await axiosInstance.get('/api/users/me/')
  return response.data
}

/**
 * Refresh JWT access token using refresh token.
 * 
 * @param {string} refreshToken - Refresh token
 * @returns {Promise<Object>} New access token
 * 
 * Educational Note: Access tokens expire quickly (e.g., 60 minutes) for security.
 * Refresh tokens last longer (e.g., 1 day) and can be used to get new access tokens
 * without requiring the user to log in again. This provides a good balance between
 * security and user experience.
 */
export async function refreshAccessToken(refreshToken) {
  const response = await axiosInstance.post('/api/token/refresh/', {
    refresh: refreshToken,
  })
  return response.data
}

/**
 * Setup two-factor authentication for current user.
 * 
 * @returns {Promise<Object>} 2FA setup data including QR code and backup tokens
 * 
 * Educational Note: This generates a TOTP secret and returns:
 * - QR code URL for scanning with authenticator apps (Google Authenticator, Authy, etc.)
 * - Backup tokens for account recovery if the user loses their device
 * The user must verify the setup by entering a code from their authenticator app.
 */
export async function setup2FA() {
  const response = await axiosInstance.post('/api/users/2fa/setup/')
  return response.data
}

/**
 * Verify 2FA setup with a code from authenticator app.
 * 
 * @param {string} code - 6-digit TOTP code
 * @param {number} deviceId - Device ID from setup response
 * @returns {Promise<Object>} Verification response
 * 
 * Educational Note: This confirms that the user successfully scanned the QR code
 * and can generate valid TOTP codes. Only after verification is 2FA enabled.
 */
export async function verify2FASetup(code, deviceId) {
  const payload = {
    token: code,  // Backend expects 'token' not 'code'
  }
  
  // Include device_id if provided (fallback to session-based approach)
  if (deviceId) {
    payload.device_id = deviceId
  }
  
  const response = await axiosInstance.post('/api/users/2fa/verify-setup/', payload)
  return response.data
}

/**
 * Verify 2FA code during login.
 * 
 * @param {string} username - Username (needed for backend verification)
 * @param {string} code - 6-digit TOTP code or backup token
 * @returns {Promise<Object>} Login response with tokens and user data
 * 
 * Educational Note: When 2FA is enabled, login is a two-step process:
 * 1. Username/password authentication (returns requires_2fa flag)
 * 2. TOTP code verification (this function)
 * This provides an additional layer of security beyond just passwords.
 */
export async function verify2FALogin(username, code) {
  const response = await axiosInstance.post('/api/users/2fa/verify-login/', {
    username,
    token: code,  // Backend expects 'token' not 'code'
  })
  return response.data
}

/**
 * Disable two-factor authentication.
 * 
 * @param {string} password - User's password for confirmation
 * @returns {Promise<Object>} Disable response
 * 
 * Educational Note: Disabling 2FA requires password confirmation for security.
 * This prevents an attacker who gains access to an authenticated session
 * from disabling 2FA without knowing the password.
 */
export async function disable2FA(password) {
  const response = await axiosInstance.post('/api/users/2fa/disable/', {
    password,
  })
  return response.data
}

/**
 * Check 2FA status for current user.
 * 
 * @returns {Promise<Object>} 2FA status (enabled/disabled)
 */
export async function check2FAStatus() {
  const response = await axiosInstance.get('/api/users/2fa/status/')
  return response.data
}

/**
 * Download backup tokens as a text file.
 * 
 * @param {Array<string>} tokens - Backup tokens to download
 * @returns {Promise<Object>} Download response with filename and content
 * 
 * Educational Note: This endpoint generates a formatted text file
 * with backup tokens that can be saved securely by the user.
 * The file includes instructions and security warnings.
 */
export async function downloadBackupTokens(tokens) {
  const response = await axiosInstance.post('/api/users/2fa/download-backup-tokens/', {
    tokens,
  })
  return response.data
}

/**
 * Regenerate backup tokens.
 * 
 * @param {string} password - User's password for confirmation
 * @returns {Promise<Object>} New backup tokens
 * 
 * Educational Note: This invalidates all old backup tokens and generates
 * new ones. Requires password confirmation for security.
 */
export async function regenerateBackupTokens(password) {
  const response = await axiosInstance.post('/api/users/2fa/regenerate-backup-tokens/', {
    password,
  })
  return response.data
}
