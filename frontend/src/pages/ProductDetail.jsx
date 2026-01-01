/**
 * Product Detail page component.
 * 
 * Educational Note: This component demonstrates:
 * - Fetching single product details from ProductService
 * - URL parameters with React Router
 * - Add to cart functionality from detail page
 * - Loading and error states
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { fetchProductById } from '../api/productService'
import Container from '../components/layout/Container'
import Button from '../components/common/Button'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorMessage from '../components/common/ErrorMessage'

function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [addedToCart, setAddedToCart] = useState(false)
  
  useEffect(() => {
    loadProduct()
  }, [id])
  
  const loadProduct = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await fetchProductById(id)
      setProduct(data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching product:', err)
      setError(err.response?.data?.detail || 'Failed to load product')
      setLoading(false)
    }
  }
  
  const handleAddToCart = () => {
    // In a real app, this would add to a global cart state
    // For now, we'll just show a success message
    setAddedToCart(true)
    setTimeout(() => setAddedToCart(false), 3000)
  }
  
  const handleQuantityChange = (delta) => {
    const newQuantity = quantity + delta
    if (newQuantity >= 1 && newQuantity <= (product?.inventory_count || 1)) {
      setQuantity(newQuantity)
    }
  }
  
  if (loading) {
    return (
      <Container maxWidth="lg" className="py-8">
        <LoadingSpinner />
      </Container>
    )
  }
  
  if (error || !product) {
    return (
      <Container maxWidth="lg" className="py-8">
        <ErrorMessage message={error || 'Product not found'} />
        <div className="mt-4">
          <Button onClick={() => navigate('/products')}>
            Back to Products
          </Button>
        </div>
      </Container>
    )
  }
  
  const isOutOfStock = product.inventory_count === 0
  
  return (
    <Container maxWidth="lg" className="py-8">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-gray-600">
        <Link to="/products" className="hover:text-blue-600">Products</Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900">{product.name}</span>
      </div>
      
      {/* Success message */}
      {addedToCart && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          ✅ Added to cart! Go to Products page to view your cart.
        </div>
      )}
      
      {/* Product Detail */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center h-96">
          <span className="text-9xl" role="img" aria-label="Product">
            📦
          </span>
        </div>
        
        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {product.name}
          </h1>
          
          <div className="mb-6">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              ${parseFloat(product.price).toFixed(2)}
            </div>
            <div
              className={`text-lg font-medium ${
                isOutOfStock ? 'text-red-600' : 'text-green-600'
              }`}
            >
              {isOutOfStock
                ? '❌ Out of stock'
                : `✅ ${product.inventory_count} in stock`}
            </div>
          </div>
          
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Description</h2>
            <p className="text-gray-700 leading-relaxed">
              {product.description}
            </p>
          </div>
          
          {/* Quantity Selector */}
          {!isOutOfStock && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity
              </label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleQuantityChange(-1)}
                  disabled={quantity <= 1}
                  className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                >
                  -
                </button>
                <span className="text-xl font-semibold w-12 text-center">
                  {quantity}
                </span>
                <button
                  onClick={() => handleQuantityChange(1)}
                  disabled={quantity >= product.inventory_count}
                  className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                >
                  +
                </button>
              </div>
            </div>
          )}
          
          {/* Actions */}
          <div className="space-y-3 mb-6">
            <div className="flex gap-3">
              <Button
                variant="primary"
                onClick={() => navigate('/orders/new', { state: { product, quantity } })}
                disabled={isOutOfStock}
                className="flex-1"
              >
                {isOutOfStock ? 'Out of Stock' : '🛒 Order Now'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/products')}
              >
                Back to Products
              </Button>
            </div>
            <Button
              variant="outline"
              onClick={handleAddToCart}
              disabled={isOutOfStock}
              className="w-full"
            >
              {isOutOfStock ? 'Out of Stock' : 'Add to Cart (Coming Soon)'}
            </Button>
          </div>
          
          {/* Product Details */}
          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Product Details</h2>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">Product ID:</dt>
                <dd className="font-medium text-gray-900">{product.id}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Category:</dt>
                <dd className="font-medium text-gray-900">{product.category || 'General'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Availability:</dt>
                <dd className="font-medium text-gray-900">
                  {isOutOfStock ? 'Out of Stock' : 'In Stock'}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
      
      {/* Educational Note */}
      <div className="mt-12 p-6 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-2">🎓 Educational Note</h3>
        <p className="text-gray-700 mb-2">
          This page demonstrates fetching a single product from ProductService with URL parameters.
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          <li>Uses React Router's useParams hook to get product ID from URL</li>
          <li>Fetches product details via REST API to ProductService</li>
          <li>Displays detailed product information with inventory status</li>
          <li>Provides quantity selector with inventory validation</li>
        </ul>
      </div>
    </Container>
  )
}

export default ProductDetail
