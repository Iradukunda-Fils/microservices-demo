/**
 * ProductCard component for displaying individual products.
 * 
 * Educational Note: This component demonstrates:
 * - Responsive card design
 * - Product information display
 * - Inventory status handling
 * - Add to cart functionality
 * - Navigation to product details
 */

import { Link } from 'react-router-dom'
import Card from '../common/Card'

/**
 * ProductCard component.
 * 
 * @param {Object} props
 * @param {Object} props.product - Product data from ProductService
 * @param {Function} props.onAddToCart - Handler for adding product to cart
 */
function ProductCard({ product, onAddToCart }) {
  const isOutOfStock = product?.inventory_count === 0 || product?.inventory_count === undefined
  
  return (
    <Card hover className="flex flex-col h-full">
      {/* Product Image Placeholder - Clickable */}
      <Link to={`/products/${product.id}`} className="block">
        <div className="h-48 bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center hover:from-blue-500 hover:to-blue-700 transition-colors">
          <span className="text-6xl" role="img" aria-label="Product">
            📦
          </span>
        </div>
      </Link>
      
      {/* Product Info */}
      <div className="p-4 flex flex-col flex-1">
        <Link to={`/products/${product.id}`} className="block mb-2 hover:text-blue-600 transition-colors">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
            {product.name}
          </h3>
        </Link>
        
        <p className="text-sm text-gray-600 mb-4 line-clamp-2 flex-1">
          {product.description}
        </p>
        
        {/* Price and Inventory */}
        <div className="flex justify-between items-center mb-4">
          <div className="text-2xl font-bold text-blue-600">
            ${parseFloat(product.price).toFixed(2)}
          </div>
          <div
            className={`text-sm font-medium ${
              isOutOfStock ? 'text-red-600' : 'text-green-600'
            }`}
          >
            {isOutOfStock
              ? 'Out of stock'
              : `${product.inventory_count ?? 0} in stock`}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onAddToCart(product)}
            disabled={isOutOfStock}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isOutOfStock ? 'Out of Stock' : 'Add to Cart'}
          </button>
          <Link to={`/products/${product.id}`}>
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-semibold whitespace-nowrap">
              Details
            </button>
          </Link>
        </div>
      </div>
    </Card>
  )
}

export default ProductCard
