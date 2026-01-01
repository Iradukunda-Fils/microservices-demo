/**
 * OrderSuccess component - displays after successful order creation.
 * 
 * Educational Note: This component provides user feedback and
 * displays the created order details. It demonstrates good UX
 * by confirming the action and providing next steps.
 */

import { Link } from 'react-router-dom'
import Card from './common/Card'
import Button from './common/Button'

function OrderSuccess({ order, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-md w-full">
        <div className="p-6">
          {/* Success Icon */}
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
          </div>
          
          {/* Success Message */}
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
            Order Placed Successfully!
          </h2>
          <p className="text-center text-gray-600 mb-6">
            Your order has been created and is being processed.
          </p>
          
          {/* Order Details */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Order ID:</span>
                <span className="font-semibold">#{order.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Amount:</span>
                <span className="font-semibold text-green-600">
                  ${parseFloat(order.total_amount).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 text-sm rounded">
                  {order.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Items:</span>
                <span className="font-semibold">{order.items?.length || 0}</span>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="space-y-3">
            <Link to="/orders" className="block">
              <Button variant="primary" className="w-full">
                View My Orders
              </Button>
            </Link>
            <Button variant="secondary" onClick={onClose} className="w-full">
              Continue Shopping
            </Button>
          </div>
          
          {/* Educational Note */}
          <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-xs text-gray-700">
              <div className="font-semibold mb-1">✅ What just happened:</div>
              <ul className="list-disc list-inside space-y-1">
                <li>Order created in OrderService database</li>
                <li>User ID encrypted with AES-256</li>
                <li>Product prices captured at purchase time</li>
                <li>Cross-service validation completed</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default OrderSuccess
