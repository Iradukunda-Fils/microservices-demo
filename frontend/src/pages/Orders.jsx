/**
 * Orders page component with order history.
 * 
 * Educational Note: This component demonstrates:
 * - Fetching user's order history from OrderService
 * - Using the API layer for clean separation
 * - Reusable components for consistent UI
 * - Order status tracking
 */

import { useState, useEffect } from 'react'
import { fetchUserOrders } from '../api/orderService'
import Container from '../components/layout/Container'
import OrderList from '../components/order/OrderList'
import ErrorMessage from '../components/common/ErrorMessage'

function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Fetch user's orders
  useEffect(() => {
    loadOrders()
  }, [])
  
  const loadOrders = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Educational Note: This calls OrderService API via our API layer
      // The backend automatically filters orders by the authenticated user's ID
      // from the JWT token. No need to pass user_id from frontend.
      const data = await fetchUserOrders()
      
      setOrders(data.results || data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching orders:', err)
      setError(err.response?.data?.detail || 'Failed to load orders')
      setLoading(false)
    }
  }
  
  return (
    <Container maxWidth="lg" className="py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Orders</h1>
        <p className="text-gray-600">
          View your order history and track your purchases
        </p>
      </div>
      
      {/* Error message */}
      <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
      
      {/* Orders list */}
      <OrderList orders={orders} loading={loading} />
      
      {/* Educational Note */}
      <div className="mt-12 p-6 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-2">🎓 Educational Note</h3>
        <p className="text-gray-700 mb-2">
          This page demonstrates fetching order history from OrderService with JWT authentication.
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          <li>User ID is extracted from JWT token (secure - can't be spoofed)</li>
          <li>Backend automatically filters orders by authenticated user</li>
          <li>User IDs are encrypted in database using AES-256</li>
          <li>Orders display with expandable details showing individual items</li>
        </ul>
      </div>
    </Container>
  )
}

export default Orders
