/**
 * Cookie utility functions for token and user data storage.
 * 
 * Educational Note: We're using JavaScript-accessible cookies instead of localStorage.
 * 
 * Why cookies over localStorage?
 * ✅ Automatic expiry via max-age
 * ✅ Can be configured as Secure (HTTPS only)
 * ✅ Can be configured with SameSite (CSRF protection)
 * ✅ Automatically sent with requests (when using credentials: 'include')
 * ✅ Better for cross-domain scenarios
 * 
 * Cookie Attributes:
 * - Secure: Only sent over HTTPS (production)
 * - SameSite=Lax: Prevents CSRF while allowing navigation
 * - Path=/: Available for all routes
 * - Max-Age: Automatic expiry
 */

/**
 * Set a cookie with security attributes.
 * 
 * @param {string} name - Cookie name
 * @param {string} value - Cookie value
 * @param {number} maxAge - Max age in seconds (optional)
 */
export function setCookie(name, value, maxAge = null) {
  let cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`
  
  // Add path
  cookie += '; path=/'
  
  // Add max-age if provided
  if (maxAge) {
    cookie += `; max-age=${maxAge}`
  }
  
  // Add SameSite for CSRF protection
  cookie += '; SameSite=Lax'
  
  // Add Secure in production (HTTPS only)
  if (window.location.protocol === 'https:') {
    cookie += '; Secure'
  }
  
  document.cookie = cookie
}

/**
 * Get a cookie value by name.
 * 
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
export function getCookie(name) {
  const nameEQ = encodeURIComponent(name) + '='
  const cookies = document.cookie.split(';')
  
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim()
    
    if (cookie.indexOf(nameEQ) === 0) {
      return decodeURIComponent(cookie.substring(nameEQ.length))
    }
  }
  
  return null
}

/**
 * Delete a cookie by name.
 * 
 * @param {string} name - Cookie name
 */
export function deleteCookie(name) {
  // Set max-age to 0 to delete immediately
  document.cookie = `${encodeURIComponent(name)}=; path=/; max-age=0`
}

/**
 * Check if a cookie exists.
 * 
 * @param {string} name - Cookie name
 * @returns {boolean} True if cookie exists
 */
export function hasCookie(name) {
  return getCookie(name) !== null
}

/**
 * Set access token cookie (15 minutes expiry).
 * 
 * Educational Note: Access tokens are short-lived for security.
 * If stolen, they're only valid for 15 minutes.
 */
export function setAccessToken(token) {
  const fifteenMinutes = 15 * 60 // 15 minutes in seconds
  setCookie('access_token', token, fifteenMinutes)
}

/**
 * Set refresh token cookie (1 day expiry).
 * 
 * Educational Note: Refresh tokens are longer-lived.
 * They're used to get new access tokens without re-login.
 */
export function setRefreshToken(token) {
  const oneDay = 24 * 60 * 60 // 1 day in seconds
  setCookie('refresh_token', token, oneDay)
}

/**
 * Set user data cookie.
 * 
 * Educational Note: We store user data as JSON string.
 * This allows the frontend to display user info without API calls.
 */
export function setUserData(user) {
  const oneDay = 24 * 60 * 60 // 1 day in seconds
  setCookie('user_data', JSON.stringify(user), oneDay)
}

/**
 * Get access token from cookie.
 */
export function getAccessToken() {
  return getCookie('access_token')
}

/**
 * Get refresh token from cookie.
 */
export function getRefreshToken() {
  return getCookie('refresh_token')
}

/**
 * Get user data from cookie.
 * 
 * @returns {Object|null} User object or null
 */
export function getUserData() {
  const userData = getCookie('user_data')
  
  if (!userData) {
    return null
  }
  
  try {
    return JSON.parse(userData)
  } catch (error) {
    console.error('Failed to parse user data from cookie:', error)
    return null
  }
}

/**
 * Clear all authentication cookies.
 * 
 * Educational Note: Called on logout to remove all auth data.
 */
export function clearAuthCookies() {
  deleteCookie('access_token')
  deleteCookie('refresh_token')
  deleteCookie('user_data')
}

/**
 * Check if user is authenticated (has access token).
 */
export function isAuthenticated() {
  return hasCookie('access_token')
}
