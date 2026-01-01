/**
 * ProductSearch component for searching products.
 * 
 * Educational Note: This component demonstrates:
 * - Controlled form input
 * - Search functionality
 * - Clear button for better UX
 */

import { useState } from 'react'

/**
 * ProductSearch component.
 * 
 * @param {Object} props
 * @param {Function} props.onSearch - Handler for search submission
 * @param {boolean} props.loading - Loading state
 */
function ProductSearch({ onSearch, loading }) {
  const [searchTerm, setSearchTerm] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(searchTerm)
  }
  
  const handleClear = () => {
    setSearchTerm('')
    onSearch('')
  }
  
  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1 relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search products..."
          className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {searchTerm && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  )
}

export default ProductSearch
