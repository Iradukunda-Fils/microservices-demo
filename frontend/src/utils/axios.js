/**
 * Axios configuration with cookie-based authentication and proactive token refresh.
 * 
 * Educational Note: Cookie-based authentication is more secure than localStorage:
 * 
 * Security Comparison:
 * 
 * localStorage (OLD):
 * ❌ Vulnerable to XSS attacks (any script can read tokens)
 * ❌ Tokens persist indefinitely
 * ❌ Manual token management required
 * ❌ Cross-tab synchronization complex
 * 
 * Cookies (NEW):
 * ✅ Automatic expiry via max-age
 * ✅ Can be configured as Secure (HTTPS only)
 * ✅ Can be configured with SameSite (CSRF protection)
 * ✅ Better cross-tab synchronization (cookie change events)
 * ✅ Automatically included in requests
 * 
 * Proactive Token Refresh:
 * ✅ Refreshes tokens BEFORE they expire (no 401 errors)
 * ✅ Checks token expiry on every request
 * ✅ Refreshes if token expires in less than 2 minutes
 * ✅ Seamless user experience (no interruptions)
 * 
 * Trade-offs:
 * - Cookies are vulnerable to CSRF attacks (mitigated by SameSite=Lax)
 * - localStorage is vulnerable to XSS attacks (no mitigation)
 * - Modern consensus: Cookies are safer for auth tokens
 * 
 * Why this approach scales in microservices:
 * - API Gateway can validate tokens once
 * - Internal services use service-to-service auth (gRPC)
 * - Consistent auth across all services
 * - Tokens automatically sent with requests
 */

import axios from 'axios'
import { getAccessToken, getRefreshToken, setAccessToken, clearAuthCookies } from './cookies'

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
  // Include credentials for CORS requests
  withCredentials: true,
})

// Track if we're currently refreshing to prevent multiple simultaneous refreshes
let isRefreshing = false
let failedQueue = []

/**
 * Process queued requests after token refresh.
 * 
 * Educational Note: When multiple requests fail simultaneously (e.g., user
 * has multiple tabs open), we queue them and process all at once after
 * a single refresh. This prevents the "refresh storm" problem.
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

/**
 * Decode JWT token to extract payload.
 * 
 * Educational Note: JWT tokens have 3 parts separated by dots:
 * header.payload.signature
 * The payload contains claims like expiration time (exp).
 */
function decodeToken(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Failed to decode token:', error)
    return null
  }
}

/**
 * Check if token is expired or will expire soon.
 * 
 * Educational Note: We refresh tokens 2 minutes before expiration
 * to prevent users from seeing 401 errors during active sessions.
 * With 15-minute tokens, this gives a 13-minute active window.
 * 
 * This is PROACTIVE refresh - we don't wait for 401 errors.
 */
function isTokenExpiringSoon(token) {
  const decoded = decodeToken(token)
  if (!decoded || !decoded.exp) return true
  
  const expirationTime = decoded.exp * 1000 // Convert to milliseconds
  const currentTime = Date.now()
  const twoMinutes = 2 * 60 * 1000 // 2 minutes buffer
  
  // Return true if token expires in less than 2 minutes
  return expirationTime - currentTime < twoMinutes
}

/**
 * Refresh access token using refresh token.
 * 
 * Educational Note: This function is called proactively BEFORE
 * the access token expires, preventing 401 errors.
 */
async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  
  if (!refreshToken) {
    return null
  }
  
  try {
    // Call DRF's token refresh endpoint
    const response = await axios.post('/api/token/refresh/', {
      refresh: refreshToken,
    })
    
    const { access } = response.data
    
    // Store new access token in cookie
    setAccessToken(access)
    
    console.log('✅ Token refreshed proactively')
    
    return access
  } catch (error) {
    console.error('❌ Token refresh failed:', error)
    
    // Clear auth cookies on refresh failure
    clearAuthCookies()
    
    // Broadcast logout to other tabs
    const channel = new BroadcastChannel('auth-channel')
    channel.postMessage({ type: 'LOGOUT' })
    channel.close()
    
    return null
  }
}

/**
 * Request interceptor.
 * Adds JWT access token from cookie to all requests.
 * Proactively refreshes token if it's expiring soon.
 * 
 * Educational Note: This is the KEY to preventing 401 errors!
 * We check token expiry BEFORE making the request and refresh if needed.
 */
axiosInstance.interceptors.request.use(
  async (config) => {
    let accessToken = getAccessToken()
    const refreshToken = getRefreshToken()
    
    // Proactively refresh token if it's expiring soon
    if (accessToken && refreshToken && isTokenExpiringSoon(accessToken)) {
      if (isRefreshing) {
        // Another request is already refreshing, wait for it
        await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
        // Get the new token after refresh completes
        accessToken = getAccessToken()
      } else {
        isRefreshing = true
        console.log('🔄 Token expiring soon, refreshing proactively...')
        
        const newToken = await refreshAccessToken()
        
        if (newToken) {
          accessToken = newToken
          processQueue(null, newToken)
        } else {
          processQueue(new Error('Token refresh failed'))
          // Redirect to login
          window.location.href = '/login'
          return Promise.reject(new Error('Token refresh failed'))
        }
        
        isRefreshing = false
      }
    }
    
    // Add token to Authorization header
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor for handling 401 errors (fallback).
 * 
 * Educational Note: This is a FALLBACK for cases where proactive
 * refresh didn't happen (e.g., token expired while request was in flight).
 * In normal operation, users should never see 401 errors.
 */
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Another request is already refreshing, wait for it
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => {
            return axiosInstance(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      const refreshToken = getRefreshToken()
      
      if (!refreshToken) {
        // No refresh token, clear auth and redirect
        isRefreshing = false
        clearAuthCookies()
        
        // Broadcast logout to other tabs
        const channel = new BroadcastChannel('auth-channel')
        channel.postMessage({ type: 'LOGOUT' })
        channel.close()
        
        window.location.href = '/login'
        return Promise.reject(error)
      }
      
      try {
        console.log('🔄 Received 401, refreshing token (fallback)...')
        
        // Call DRF's token refresh endpoint
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken,
        })
        
        const { access } = response.data
        
        // Store new access token in cookie
        setAccessToken(access)
        
        // Refresh successful, process queued requests
        processQueue(null, access)
        isRefreshing = false
        
        // Update the failed request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`
        
        // Retry original request
        return axiosInstance(originalRequest)
        
      } catch (refreshError) {
        // Refresh failed, clear auth state and redirect to login
        console.error('❌ Token refresh failed (fallback):', refreshError)
        processQueue(refreshError)
        isRefreshing = false
        clearAuthCookies()
        
        // Broadcast logout to other tabs
        const channel = new BroadcastChannel('auth-channel')
        channel.postMessage({ type: 'LOGOUT' })
        channel.close()
        
        // Redirect to login
        window.location.href = '/login'
        
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default axiosInstance
