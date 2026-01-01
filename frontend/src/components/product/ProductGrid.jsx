/**
 * ProductGrid component for displaying products in a responsive grid.
 * 
 * Educational Note: This component demonstrates:
 * - Responsive grid layout (1 col mobile, 2 tablet, 3-4 desktop)
 * - Loading and empty states
 * - Reusable product display
 */

import ProductCard from './ProductCard'
import LoadingSpinner from '../common/LoadingSpinner'

/**
 * ProductGrid component.
 * 
 * @param {Object} props
 * @param {Array} props.products - Array of products from ProductService
 * @param {boolean} props.loading - Loading state
 * @param {Function} props.onAddToCart - Handler for adding product to cart
 */
function ProductGrid({ products, loading, onAddToCart }) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="large" />
      </div>
    )
  }
  
  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          No products found
        </h3>
        <p className="text-gray-600">
          Try adjusting your search or filters
        </p>
      </div>
    )
  }
  
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  )
}

export default ProductGrid
