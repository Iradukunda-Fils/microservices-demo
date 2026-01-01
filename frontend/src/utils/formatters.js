/**
 * Utility functions for formatting data.
 * 
 * Educational Note: Extracting formatting logic into utility functions
 * promotes code reuse and makes components cleaner.
 */

/**
 * Format a number as currency (USD).
 * 
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount) {
  return `$${parseFloat(amount).toFixed(2)}`
}

/**
 * Format a date string for display.
 * 
 * @param {string} dateString - ISO date string
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateString, options = {}) {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { ...defaultOptions, ...options })
}

/**
 * Format order status for display.
 * 
 * @param {string} status - Order status
 * @returns {string} Formatted status string
 */
export function formatStatus(status) {
  if (!status) return ''
  return status.charAt(0).toUpperCase() + status.slice(1)
}

/**
 * Get Tailwind color classes for order status.
 * 
 * @param {string} status - Order status
 * @returns {string} Tailwind CSS classes
 */
export function getStatusColorClasses(status) {
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
