/**
 * OrderForm component for creating orders.
 * 
 * Educational Note: This component demonstrates:
 * - Order creation via OrderService API
 * - Cross-service validation (user + products)
 * - Error handling for various failure scenarios
 * - Success feedback
 * - Cart to order conversion
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createOrder } from '../api/orderService'

function OrderForm({ cart, onSuccess, onCancel }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [createdOrder, setCreatedOrder] = useState(null)
  const navigate = useNavigate()
  
  // Calculate total
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      // Educational Note: This calls OrderService API
      // OrderService will:
      // 1. Get user_id from JWT token (secure - can't be spoofed)
      // 2. Validate user exists (via gRPC to UserService)
      // 3. Validate products exist (via gRPC to ProductService)
      // 4. Check inventory availability (via gRPC to ProductService)
      // 5. Create order with encrypted user_id
      // 6. Create order items
      // 
      // This demonstrates the orchestration pattern in microservices!
      // Security: user_id comes from JWT token, not client input.
      
      const orderData = {
        items: cart.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
      }
      
      console.log('📦 Sending order data:', JSON.stringify(orderData, null, 2))
      
      const response = await createOrder(orderData)
      
      // Success!
      setLoading(false)
      setSuccess(true)
      setCreatedOrder(response)
      onSuccess(response)
      
    } catch (err) {
      console.error('Order creation error:', err)
      console.error('Error response:', err.response)
      console.error('Error response data:', err.response?.data)
      setLoading(false)
      
      // Educational Note: Different error types from OrderService
      if (err.response?.status === 400) {
        // Validation error (invalid user, product not found, insufficient inventory)
        const errorDetail = err.response.data.detail || err.response.data.error || 'Validation failed'
        console.error('Validation error detail:', errorDetail)
        setError(JSON.stringify(errorDetail, null, 2))
      } else if (err.response?.status === 503) {
        // Service unavailable (circuit breaker open, gRPC error)
        setError('Service temporarily unavailable. Please try again later.')
      } else {
        setError('Failed to create order. Please try again.')
      }
    }
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {success ? 'Order Placed Successfully!' : 'Confirm Order'}
          </h2>
          
          {/* Success message */}
          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
              <div className="font-semibold mb-2">✅ Order Created Successfully!</div>
              <div className="text-sm mb-4">
                Order #{createdOrder?.id} has been placed. Total: ${parseFloat(createdOrder?.total_amount || 0).toFixed(2)}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => navigate('/orders')}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
                >
                  View My Orders
                </button>
                <button
                  onClick={onCancel}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold"
                >
                  Continue Shopping
                </button>
              </div>
            </div>
          )}
          
          {/* Error message */}
          {error && !success && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <div className="font-semibold mb-1">Order Failed</div>
              <div>{error}</div>
            </div>
          )}
          
          {/* Order form content - hide when success */}
          {!success && (
            <>
              {/* Order Summary */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-4">Order Summary</h3>
                <div className="space-y-3">
                  {cart.map(item => (
                    <div key={item.product_id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <div className="flex-1">
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-gray-600">
                          ${parseFloat(item.price).toFixed(2)} × {item.quantity}
                        </div>
                      </div>
                      <div className="font-semibold">
                        ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Total */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Total Amount:</span>
                  <span className="text-2xl font-bold text-blue-600">
                    ${total.toFixed(2)}
                  </span>
                </div>
              </div>
              
              {/* Educational Note */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-sm text-gray-700">
                  <div className="font-semibold mb-2">🎓 What happens when you place this order:</div>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>OrderService validates your user account (via JWT from Authorization Header)</li>
                    <li>OrderService validates products exist (via gRPC to ProductService)</li>
                    <li>OrderService checks inventory availability (via gRPC to ProductService)</li>
                    <li>OrderService creates order with encrypted user_id (AES-256)</li>
                    <li>OrderService creates order items with price snapshots</li>
                  </ol>
                  <div className="mt-2 text-xs text-gray-600">
                    This demonstrates microservices orchestration with retry logic and circuit breaker!
                  </div>
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={onCancel}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Order...
                    </span>
                  ) : (
                    'Place Order'
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default OrderForm
