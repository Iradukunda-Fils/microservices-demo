/**
 * Main App component with routing and authentication context.
 * 
 * Educational Note: This component demonstrates:
 * - React Router for navigation
 * - Context API for global state (authentication)
 * - Protected routes (require authentication)
 * - Public routes (redirect if already authenticated)
 * - Layout components
 * 
 * Security Features:
 * - Route guards prevent unauthorized access
 * - Authenticated users redirected away from login/register
 * - Post-login redirect to intended destination
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import PublicRoute from './components/auth/PublicRoute'
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import Orders from './pages/Orders'
import NewOrder from './pages/NewOrder'
import TwoFactorSetup from './pages/TwoFactorSetup'

/**
 * Main App component.
 */
function App() {
  return (
    <AuthProvider>
      <Router future={{ v7_relativeSplatPath: true }}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              
              {/* Public routes - redirect to products if already authenticated */}
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                }
              />
              
              {/* Protected routes - require authentication */}
              <Route
                path="/products"
                element={
                  <ProtectedRoute>
                    <Products />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/products/:id"
                element={
                  <ProtectedRoute>
                    <ProductDetail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders"
                element={
                  <ProtectedRoute>
                    <Orders />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/orders/new"
                element={
                  <ProtectedRoute>
                    <NewOrder />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/2fa-setup"
                element={
                  <ProtectedRoute>
                    <TwoFactorSetup />
                  </ProtectedRoute>
                }
              />
              
              {/* Catch-all route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
