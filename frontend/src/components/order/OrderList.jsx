/**
 * OrderList component for displaying a list of orders.
 * 
 * Educational Note: This component demonstrates:
 * - List rendering with proper keys
 * - Loading and empty states
 * - Reusable order display
 */

import OrderCard from './OrderCard'
import LoadingSpinner from '../common/LoadingSpinner'
import { Link } from 'react-router-dom'

/**
 * OrderList component.
 * 
 * @param {Object} props
 * @param {Array} props.orders - Array of orders from OrderService
 * @param {boolean} props.loading - Loading state
 */
function OrderList({ orders, loading }) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }
  
  if (orders.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📦</div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          No orders yet
        </h2>
        <p className="text-gray-600 mb-6">
          Start shopping to see your orders here!
        </p>
        <Link
          to="/products"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          Browse Products
        </Link>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  )
}

export default OrderList
