/**
 * PublicRoute component for login/register pages.
 * 
 * Educational Note: This component redirects authenticated users away from
 * login/register pages. This prevents confusion and improves UX.
 * 
 * Example: If user is already logged in and tries to access /login,
 * they're redirected to /products instead.
 */

import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  
  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }
  
  // If user is authenticated, redirect to intended destination or products page
  if (isAuthenticated) {
    // Check if there's a saved destination from ProtectedRoute
    const from = location.state?.from?.pathname || '/products'
    return <Navigate to={from} replace />
  }
  
  // User is not authenticated, show public page (login/register)
  return children
}

export default PublicRoute
