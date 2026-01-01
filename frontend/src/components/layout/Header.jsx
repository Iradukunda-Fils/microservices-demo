/**
 * Header component with navigation using Tailwind CSS.
 * 
 * Educational Note: This component demonstrates:
 * - Responsive navigation with mobile menu
 * - Conditional rendering based on authentication state
 * - Tailwind utility classes for styling
 */

import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useState } from 'react'

function Header() {
  const { isAuthenticated, user, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 text-gray-900 hover:text-blue-600 transition-colors">
            <span className="text-2xl">🏪</span>
            <h1 className="text-xl font-bold hidden sm:block">Microservices Demo</h1>
            <h1 className="text-xl font-bold sm:hidden">MS Demo</h1>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {isAuthenticated ? (
              <>
                <Link to="/products" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  Products
                </Link>
                <Link to="/orders" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  My Orders
                </Link>
                <Link to="/2fa-setup" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  2FA Setup
                </Link>
                <span className="text-gray-600 flex items-center">
                  <span className="mr-1">👤</span>
                  <span className="font-medium">{user?.username}</span>
                </span>
                <button
                  onClick={logout}
                  className="btn btn-secondary"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary">
                  Register
                </Link>
              </>
            )}
          </nav>
          
          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
        
        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 animate-fade-in">
            <nav className="flex flex-col space-y-3">
              {isAuthenticated ? (
                <>
                  <div className="px-4 py-2 bg-gray-50 rounded-lg">
                    <span className="text-gray-600 flex items-center">
                      <span className="mr-2">👤</span>
                      <span className="font-medium">{user?.username}</span>
                    </span>
                  </div>
                  <Link
                    to="/products"
                    className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Products
                  </Link>
                  <Link
                    to="/orders"
                    className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    My Orders
                  </Link>
                  <Link
                    to="/2fa-setup"
                    className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    2FA Setup
                  </Link>
                  <button
                    onClick={() => {
                      logout()
                      setMobileMenuOpen(false)
                    }}
                    className="btn btn-secondary w-full"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="btn btn-primary w-full"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Register
                  </Link>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
