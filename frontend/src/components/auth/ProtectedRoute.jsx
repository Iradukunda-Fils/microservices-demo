/**
 * ProtectedRoute component for route-level authentication.
 * 
 * Educational Note: This component implements route guards, a common pattern
 * in authentication systems. It prevents unauthorized access to protected pages.
 * 
 * Security Features:
 * - Redirects unauthenticated users to login
 * - Preserves intended destination for post-login redirect
 * - Shows loading state during auth check
 * - Prevents flash of protected content
 */

import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  
  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    )
  }
  
  // Redirect to login if not authenticated
  // Save the current location to redirect back after login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  // User is authenticated, render protected content
  return children
}

export default ProtectedRoute
