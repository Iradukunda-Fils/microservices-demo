/**
 * Home page component.
 * 
 * Educational Note: Landing page that explains the microservices demo project.
 * This showcases what the application does and guides users to register or login.
 */

import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Container from '../components/layout/Container'
import Button from '../components/common/Button'

function Home() {
  const { isAuthenticated } = useAuth()
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <Container maxWidth="2xl" className="py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to Microservices Demo
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            A production-ready microservices architecture demonstration
          </p>
          
          {!isAuthenticated && (
            <div className="flex gap-4 justify-center">
              <Link to="/register">
                <Button variant="primary" className="px-8 py-3 text-lg">
                  Get Started
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="secondary" className="px-8 py-3 text-lg">
                  Login
                </Button>
              </Link>
            </div>
          )}
          
          {isAuthenticated && (
            <div className="flex gap-4 justify-center">
              <Link to="/products">
                <Button variant="primary" className="px-8 py-3 text-lg">
                  Browse Products
                </Button>
              </Link>
              <Link to="/orders">
                <Button variant="secondary" className="px-8 py-3 text-lg">
                  View Orders
                </Button>
              </Link>
            </div>
          )}
        </div>
      </Container>
      
      {/* Features Section */}
      <Container maxWidth="2xl" className="py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          What This Demo Showcases
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">🔐</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              JWT Authentication
            </h3>
            <p className="text-gray-600">
              RSA-based JWT tokens (RS256) with public/private key architecture.
              UserService signs tokens, other services verify them locally.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Two-Factor Authentication
            </h3>
            <p className="text-gray-600">
              TOTP-based 2FA with QR codes for authenticator apps.
              Includes backup tokens for account recovery.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              gRPC Communication
            </h3>
            <p className="text-gray-600">
              High-performance inter-service communication using gRPC.
              7-10x faster than REST for internal calls.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">🔄</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Resilience Patterns
            </h3>
            <p className="text-gray-600">
              Retry logic with exponential backoff and circuit breaker pattern.
              Handles failures gracefully without cascading.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">🔐</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Field-Level Encryption
            </h3>
            <p className="text-gray-600">
              Sensitive data encrypted at application layer using AES-256.
              Defense-in-depth security strategy.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-5xl mb-4">🏗️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Service Isolation
            </h3>
            <p className="text-gray-600">
              Each microservice has its own database.
              No direct database access between services.
            </p>
          </div>
        </div>
      </Container>
      
      {/* Architecture Section */}
      <Container maxWidth="2xl" className="py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Architecture Overview
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">UserService</h3>
            <p className="text-blue-100 mb-4">
              Authentication, user management, 2FA
            </p>
            <p className="text-sm text-blue-200">
              Django • JWT • gRPC
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">ProductService</h3>
            <p className="text-green-100 mb-4">
              Product catalog, inventory management
            </p>
            <p className="text-sm text-green-200">
              Django • DRF • gRPC
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">OrderService</h3>
            <p className="text-purple-100 mb-4">
              Order orchestration, cross-service validation
            </p>
            <p className="text-sm text-purple-200">
              Django • Tenacity • PyBreaker
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">Frontend</h3>
            <p className="text-orange-100 mb-4">
              React SPA with JWT authentication
            </p>
            <p className="text-sm text-orange-200">
              React • Axios • React Router
            </p>
          </div>
        </div>
      </Container>
      
      {/* CTA Section */}
      <Container maxWidth="2xl" className="py-16">
        <div className="bg-blue-600 text-white rounded-lg shadow-xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
          <p className="text-xl text-blue-100 mb-8">
            {isAuthenticated
              ? 'Browse products and create orders to see the microservices in action!'
              : 'Register an account to start exploring the demo application.'}
          </p>
          {!isAuthenticated && (
            <Link to="/register">
              <Button variant="secondary" className="px-8 py-3 text-lg bg-white text-blue-600 hover:bg-gray-100">
                Create Account
              </Button>
            </Link>
          )}
        </div>
      </Container>
    </div>
  )
}

export default Home
