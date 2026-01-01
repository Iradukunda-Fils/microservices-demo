/**
 * Authentication Context with cookie-based auth and cross-tab sync.
 * 
 * Educational Note: This context uses cookies instead of localStorage.
 * 
 * Why cookies over localStorage?
 * ✅ Automatic expiry via max-age
 * ✅ Can be configured as Secure (HTTPS only)
 * ✅ Can be configured with SameSite (CSRF protection)
 * ✅ Better cross-tab synchronization
 * ✅ Automatically sent with requests
 * 
 * Cross-tab synchronization:
 * - Uses BroadcastChannel API (modern browsers)
 * - When user logs in/out in one tab, all tabs update
 * - No polling required, event-driven
 * 
 * Why this is better:
 * - Tokens have automatic expiry
 * - Better security with Secure and SameSite attributes
 * - Consistent state across tabs
 * - Simpler token management
 */

import { createContext, useContext, useState, useEffect } from 'react'
import * as userService from '../api/userService'
import {
  getUserData,
  setAccessToken,
  setRefreshToken,
  setUserData,
  clearAuthCookies,
  isAuthenticated as checkIsAuthenticated,
} from '../utils/cookies'

const AuthContext = createContext(null)

/**
 * Custom hook to use the auth context.
 * Throws error if used outside AuthProvider.
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

/**
 * AuthProvider component that wraps the app and provides auth state.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Educational Note: Load user from cookie on mount
  // This persists authentication across page refreshes
  useEffect(() => {
    const userData = getUserData()
    
    if (userData && checkIsAuthenticated()) {
      setUser(userData)
    }
    
    setLoading(false)
  }, [])
  
  // Educational Note: Cross-tab synchronization
  // Listen for auth events from other tabs using BroadcastChannel
  useEffect(() => {
    const channel = new BroadcastChannel('auth-channel')
    
    channel.onmessage = (event) => {
      if (event.data.type === 'LOGIN') {
        setUser(event.data.user)
      } else if (event.data.type === 'LOGOUT') {
        setUser(null)
        // Optionally redirect to login
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login'
        }
      }
    }
    
    return () => channel.close()
  }, [])
  
  /**
   * Login function.
   * Stores tokens and user data in cookies.
   * 
   * Educational Note: Cookies provide automatic expiry and better security.
   * Access token expires in 15 minutes, refresh token in 1 day.
   * 
   * Two-step login flow:
   * 1. If 2FA disabled: Returns tokens immediately
   * 2. If 2FA enabled: Returns requires2FA flag, then call verify2FALogin
   */
  const login = async (username, password) => {
    try {
      const data = await userService.loginUser({ username, password })
      
      // Check if 2FA is required
      if (data.requires_2fa) {
        return {
          success: true,
          requires2FA: true,
          username: data.username,  // Store username for 2FA verification
        }
      }
      
      // No 2FA - normal login flow
      const { access, refresh, user: userData } = data
      
      // Store tokens in cookies
      setAccessToken(access)
      setRefreshToken(refresh)
      setUserData(userData)
      
      // Update state
      setUser(userData)
      
      // Broadcast login to other tabs
      const channel = new BroadcastChannel('auth-channel')
      channel.postMessage({ type: 'LOGIN', user: userData })
      channel.close()
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }
  
  /**
   * Logout function.
   * Clears tokens and user data from cookies.
   * 
   * Educational Note: Cookies are automatically deleted when max-age expires,
   * but we manually clear them on logout for immediate effect.
   */
  const logout = () => {
    // Clear cookies
    clearAuthCookies()
    
    // Clear state
    setUser(null)
    
    // Broadcast logout to other tabs
    const channel = new BroadcastChannel('auth-channel')
    channel.postMessage({ type: 'LOGOUT' })
    channel.close()
  }
  
  /**
   * Register new user.
   */
  const register = async (username, email, password) => {
    try {
      const data = await userService.registerUser({ username, email, password })
      
      return { success: true, data }
    } catch (error) {
      console.error('Registration error:', error)
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      }
    }
  }
  
  /**
   * Setup 2FA for the current user.
   * Returns QR code and backup tokens.
   */
  const setup2FA = async () => {
    try {
      const data = await userService.setup2FA()
      
      return { success: true, data }
    } catch (error) {
      console.error('2FA setup error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || '2FA setup failed',
      }
    }
  }
  
  /**
   * Verify 2FA setup with a code.
   */
  const verify2FASetup = async (code, deviceId) => {
    try {
      const data = await userService.verify2FASetup(code, deviceId)
      
      return { success: true, data }
    } catch (error) {
      console.error('2FA verification error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.error || '2FA verification failed',
      }
    }
  }
  
  /**
   * Verify 2FA code during login.
   * Completes the two-step login process.
   */
  const verify2FALogin = async (username, code) => {
    try {
      const data = await userService.verify2FALogin(username, code)
      
      const { access, refresh, user: userData } = data
      
      // Store tokens in cookies
      setAccessToken(access)
      setRefreshToken(refresh)
      setUserData(userData)
      
      // Update state
      setUser(userData)
      
      // Broadcast login to other tabs
      const channel = new BroadcastChannel('auth-channel')
      channel.postMessage({ type: 'LOGIN', user: userData })
      channel.close()
      
      return { success: true, data }
    } catch (error) {
      console.error('2FA login verification error:', error)
      return {
        success: false,
        error: error.response?.data?.message || error.response?.data?.error || '2FA verification failed',
      }
    }
  }
  
  /**
   * Disable 2FA for the current user.
   */
  const disable2FA = async (password) => {
    try {
      const data = await userService.disable2FA(password)
      
      return { success: true, data }
    } catch (error) {
      console.error('2FA disable error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to disable 2FA',
      }
    }
  }
  
  /**
   * Check 2FA status for the current user.
   */
  const check2FAStatus = async () => {
    try {
      const data = await userService.check2FAStatus()
      
      return { success: true, data }
    } catch (error) {
      console.error('2FA status check error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to check 2FA status',
      }
    }
  }
  
  const value = {
    user,
    isAuthenticated: !!user && checkIsAuthenticated(),
    login,
    logout,
    register,
    setup2FA,
    verify2FASetup,
    verify2FALogin,
    disable2FA,
    check2FAStatus,
    loading,
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    )
  }
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
