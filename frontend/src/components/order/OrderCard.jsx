/**
 * OrderCard component for displaying individual orders.
 * 
 * Educational Note: This component demonstrates:
 * - Order information display with all backend fields
 * - Status color coding with visual indicators
 * - Expandable order items with detailed breakdown
 * - Professional date and currency formatting
 * - Null-safe data handling
 */

import { useState } from 'react'
import Card from '../common/Card'

/**
 * OrderCard component.
 * 
 * @param {Object} props
 * @param {Object} props.order - Order data from OrderService
 * @param {number} props.order.id - Order ID
 * @param {string} props.order.user_id - User ID (from JWT)
 * @param {string} props.order.total_amount - Total order amount
 * @param {string} props.order.status - Order status (pending, confirmed, etc.)
 * @param {Array} props.order.items - Array of order items
 * @param {string} props.order.created_at - ISO timestamp
 * @param {string} props.order.updated_at - ISO timestamp
 */
function OrderCard({ order }) {
  const [expanded, setExpanded] = useState(false)
  
  // Safely parse numeric values
  const totalAmount = parseFloat(order?.total_amount || 0)
  const itemCount = order?.items?.length || 0
  
  // Format date with fallback
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch (error) {
      return 'Invalid date'
    }
  }
  
  // Format currency
  const formatCurrency = (amount) => {
    const value = parseFloat(amount || 0)
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }
  
  // Get status color and icon
  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      confirmed: 'bg-blue-100 text-blue-800 border-blue-200',
      processing: 'bg-purple-100 text-purple-800 border-purple-200',
      shipped: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      delivered: 'bg-green-100 text-green-800 border-green-200',
      cancelled: 'bg-red-100 text-red-800 border-red-200',
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200'
  }
  
  // Get status icon
  const getStatusIcon = (status) => {
    const icons = {
      pending: '⏳',
      confirmed: '✓',
      processing: '⚙️',
      shipped: '🚚',
      delivered: '✅',
      cancelled: '❌',
    }
    return icons[status] || '📦'
  }
  
  // Validate order data
  if (!order || !order.id) {
    return (
      <Card>
        <div className="p-6 text-center text-gray-500">
          Invalid order data
        </div>
      </Card>
    )
  }
  
  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      {/* Order Header */}
      <div
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors duration-150"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex flex-wrap justify-between items-start gap-4">
          {/* Left Section: Order Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <h3 className="text-lg font-semibold text-gray-900">
                Order #{order.id}
              </h3>
              <span
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(
                  order.status
                )}`}
              >
                <span>{getStatusIcon(order.status)}</span>
                <span>{order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>
              </span>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Placed:</span> {formatDate(order.created_at)}
              </p>
              {order.updated_at && order.updated_at !== order.created_at && (
                <p className="text-xs text-gray-500">
                  <span className="font-medium">Updated:</span> {formatDate(order.updated_at)}
                </p>
              )}
            </div>
          </div>
          
          {/* Right Section: Amount & Items */}
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              ${formatCurrency(totalAmount)}
            </div>
            <p className="text-sm text-gray-600 mb-2">
              {itemCount} {itemCount === 1 ? 'item' : 'items'}
            </p>
            <button 
              className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
              onClick={(e) => {
                e.stopPropagation()
                setExpanded(!expanded)
              }}
            >
              <span>{expanded ? '▲ Hide' : '▼ Show'} Details</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Order Details (Expandable) */}
      {expanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          {/* Order Items */}
          {order.items && order.items.length > 0 ? (
            <div className="p-6">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>📦</span>
                <span>Order Items ({itemCount})</span>
              </h4>
              <div className="space-y-3">
                {order.items.map((item, index) => {
                  const itemSubtotal = parseFloat(item?.subtotal || 0)
                  const itemPrice = parseFloat(item?.price_at_purchase || 0)
                  const itemQuantity = parseInt(item?.quantity || 0)
                  
                  return (
                    <div
                      key={item?.id || index}
                      className="flex justify-between items-start bg-white p-4 rounded-lg shadow-sm border border-gray-100"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-medium text-gray-500">
                            Item #{index + 1}
                          </span>
                          <span className="text-xs text-gray-400">
                            (ID: {item?.product_id || 'N/A'})
                          </span>
                        </div>
                        <div className="font-medium text-gray-900 mb-1">
                          Product ID: {item?.product_id || 'Unknown'}
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Quantity:</span>
                            <span>{itemQuantity}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Unit Price:</span>
                            <span>${formatCurrency(itemPrice)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Calculation:</span>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {itemQuantity} × ${formatCurrency(itemPrice)} = ${formatCurrency(itemSubtotal)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-xs text-gray-500 mb-1">Subtotal</div>
                        <div className="text-lg font-bold text-gray-900">
                          ${formatCurrency(itemSubtotal)}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              
              {/* Order Summary */}
              <div className="mt-6 pt-4 border-t border-gray-300">
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm text-gray-600">
                    <span>Items Total ({itemCount} items):</span>
                    <span className="font-medium">${formatCurrency(totalAmount)}</span>
                  </div>
                  <div className="flex justify-between items-center text-lg font-bold pt-2 border-t border-gray-200">
                    <span className="text-gray-900">Order Total:</span>
                    <span className="text-blue-600 text-2xl">
                      ${formatCurrency(totalAmount)}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Order Metadata */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Order Information
                </h5>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-500">Order ID:</span>
                    <span className="ml-2 font-medium text-gray-900">#{order.id}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {formatDate(order.created_at)}
                    </span>
                  </div>
                  {order.updated_at && order.updated_at !== order.created_at && (
                    <div>
                      <span className="text-gray-500">Last Updated:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {formatDate(order.updated_at)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-gray-500">
              No items in this order
            </div>
          )}
        </div>
      )}
    </Card>
  )
}

export default OrderCard
