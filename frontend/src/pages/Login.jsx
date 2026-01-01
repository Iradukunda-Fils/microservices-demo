/**
 * Login page component with 2FA support.
 * 
 * Educational Note: This component demonstrates a two-step login process:
 * 1. Username/password authentication
 * 2. 2FA code verification (if enabled)
 * 
 * The backend returns a flag indicating if 2FA is required.
 * If so, we show a second form for the 6-digit code.
 */

import { useState } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Container from '../components/layout/Container'
import Button from '../components/common/Button'
import ErrorMessage from '../components/common/ErrorMessage'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [requires2FA, setRequires2FA] = useState(false)
  const [storedUsername, setStoredUsername] = useState('')  // Store username for 2FA verification
  
  const { login, verify2FALogin } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  // Check for success message from registration
  const registrationMessage = location.state?.message
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    const result = await login(username, password)
    
    if (result.success) {
      // Check if 2FA is required
      if (result.requires2FA) {
        setRequires2FA(true)
        setStoredUsername(result.username || username)  // Store username for 2FA step
      } else {
        // Login successful, no 2FA required
        // Redirect to intended destination or products page
        const from = location.state?.from?.pathname || '/products'
        navigate(from, { replace: true })
      }
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }
  
  const handle2FASubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    const result = await verify2FALogin(storedUsername, twoFactorCode)
    
    if (result.success) {
      // Redirect to intended destination or products page
      const from = location.state?.from?.pathname || '/products'
      navigate(from, { replace: true })
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }
  
  if (requires2FA) {
    return (
      <Container maxWidth="sm" className="py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Two-Factor Authentication</h2>
          
          <p className="text-gray-600 mb-6">
            Enter the 6-digit code from your authenticator app.
          </p>
          
          <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
          
          <form onSubmit={handle2FASubmit} className="space-y-6">
            <div>
              <label htmlFor="twoFactorCode" className="block text-sm font-medium text-gray-700 mb-2">
                Authentication Code or Backup Token
              </label>
              <input
                type="text"
                id="twoFactorCode"
                value={twoFactorCode}
                onChange={(e) => setTwoFactorCode(e.target.value)}
                placeholder="6-digit code or backup token"
                maxLength="32"
                required
                autoComplete="off"
                autoFocus
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-lg tracking-wider font-mono"
              />
              <p className="mt-2 text-xs text-gray-500 text-center">
                Enter 6-digit code from app OR 32-character backup token
              </p>
            </div>
            
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={twoFactorCode.length < 6}
              className="w-full"
            >
              Verify
            </Button>
          </form>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
            <p className="mb-3 font-semibold text-gray-900">
              💡 How to use backup tokens:
            </p>
            <ol className="list-decimal list-inside space-y-2 mb-3">
              <li>Enter one of your 10 backup tokens (32 characters)</li>
              <li>Each token can only be used once</li>
              <li>After using a token, you'll have 9 remaining</li>
            </ol>
            <p className="mb-2">
              <strong>Lost your phone?</strong> Use a backup token instead of the 6-digit code.
            </p>
            <p>
              <strong>Can't access your codes?</strong> Contact support for help.
            </p>
          </div>
          
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setRequires2FA(false)
                setTwoFactorCode('')
                setStoredUsername('')
              }}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              ← Back to login
            </button>
          </div>
        </div>
      </Container>
    )
  }
  
  return (
    <Container maxWidth="sm" className="py-12">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Login</h2>
        
        {registrationMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {registrationMessage}
          </div>
        )}
        
        <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              placeholder="Enter your username"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="Enter your password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            className="w-full"
          >
            Login
          </Button>
        </form>
        
        <p className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
            Register here
          </Link>
        </p>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm font-semibold text-gray-900 mb-2">Demo Credentials:</p>
          <p className="text-sm text-gray-700">Username: <code className="bg-white px-2 py-1 rounded">user0</code></p>
          <p className="text-sm text-gray-700">Password: <code className="bg-white px-2 py-1 rounded">password123</code></p>
          <p className="text-xs text-gray-600 mt-2">
            (2FA not enabled by default - you can enable it after logging in)
          </p>
        </div>
      </div>
    </Container>
  )
}

export default Login
