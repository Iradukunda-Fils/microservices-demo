/**
 * New Order page component.
 * 
 * Educational Note: This component demonstrates:
 * - Creating orders from product detail page
 * - Handling location state from navigation
 * - Single-product order flow
 */

import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { createOrder } from '../api/orderService'
import Container from '../components/layout/Container'
import Button from '../components/common/Button'
import ErrorMessage from '../components/common/ErrorMessage'

function NewOrder() {
  const navigate = useNavigate()
  const location = useLocation()
  const { product, quantity } = location.state || {}
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [createdOrder, setCreatedOrder] = useState(null)
  
  // Redirect if no product data
  useEffect(() => {
    if (!product) {
      navigate('/products')
    }
  }, [product, navigate])
  
  if (!product) {
    return null
  }
  
  const total = parseFloat(product.price) * quantity
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const orderData = {
        items: [{
          product_id: product.id,
          quantity: quantity,
        }],
      }
      
      console.log('📦 Creating order:', JSON.stringify(orderData, null, 2))
      
      const response = await createOrder(orderData)
      
      setLoading(false)
      setSuccess(true)
      setCreatedOrder(response)
      
    } catch (err) {
      console.error('Order creation error:', err)
      setLoading(false)
      
      if (err.response?.status === 400) {
        const errorDetail = err.response.data.detail || err.response.data.error || 'Validation failed'
        setError(typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail, null, 2))
      } else if (err.response?.status === 503) {
        setError('Service temporarily unavailable. Please try again later.')
      } else {
        setError('Failed to create order. Please try again.')
      }
    }
  }
  
  return (
    <Container maxWidth="lg" className="py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          {success ? 'Order Placed Successfully!' : 'Confirm Your Order'}
        </h1>
        
        {/* Success message */}
        {success && (
          <div className="mb-6 p-6 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-green-700">
              <div className="font-semibold text-xl mb-2">✅ Order Created Successfully!</div>
              <div className="mb-4">
                Order #{createdOrder?.id} has been placed.
              </div>
              <div className="text-lg font-semibold mb-4">
                Total: ${parseFloat(createdOrder?.total_amount || 0).toFixed(2)}
              </div>
              <div className="flex gap-3">
                <Button
                  onClick={() => navigate('/orders')}
                  variant="primary"
                  className="flex-1"
                >
                  View My Orders
                </Button>
                <Button
                  onClick={() => navigate('/products')}
                  variant="secondary"
                  className="flex-1"
                >
                  Continue Shopping
                </Button>
              </div>
            </div>
          </div>
        )}
        
        {/* Error message */}
        <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
        
        {/* Order form - hide when success */}
        {!success && (
          <div className="bg-white rounded-lg shadow-md p-6">
            {/* Order Summary */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start gap-4">
                  <div className="text-4xl">📦</div>
                  <div className="flex-1">
                    <div className="font-semibold text-lg">{product.name}</div>
                    <div className="text-gray-600 mt-1">{product.description}</div>
                    <div className="mt-3 flex items-center gap-4">
                      <div className="text-sm text-gray-600">
                        Price: <span className="font-semibold">${parseFloat(product.price).toFixed(2)}</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Quantity: <span className="font-semibold">{quantity}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-600">Subtotal</div>
                    <div className="text-xl font-bold text-gray-900">
                      ${total.toFixed(2)}
                    </div>
                  </div>
                </div>
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
                  <li>OrderService validates your user account (via JWT)</li>
                  <li>OrderService validates product exists (via gRPC to ProductService)</li>
                  <li>OrderService checks inventory availability</li>
                  <li>OrderService creates order with encrypted user_id</li>
                  <li>OrderService creates order item with price snapshot</li>
                </ol>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex gap-3">
              <Button
                onClick={() => navigate(-1)}
                disabled={loading}
                variant="secondary"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={loading}
                loading={loading}
                variant="primary"
                className="flex-1"
              >
                Place Order
              </Button>
            </div>
          </div>
        )}
      </div>
    </Container>
  )
}

export default NewOrder
