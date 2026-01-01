/**
 * Products page component with product listing.
 * 
 * Educational Note: This component demonstrates:
 * - Fetching data from ProductService API
 * - Loading and error states
 * - Product grid layout
 * - Search and filtering
 * - Pagination
 * - Add to cart functionality (for order creation)
 */

import { useState, useEffect } from 'react'
import { fetchProducts } from '../api/productService'
import Container from '../components/layout/Container'
import ProductGrid from '../components/product/ProductGrid'
import ProductSearch from '../components/product/ProductSearch'
import ErrorMessage from '../components/common/ErrorMessage'
import Button from '../components/common/Button'
import OrderForm from '../components/OrderForm'
import OrderSuccess from '../components/OrderSuccess'

function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [cart, setCart] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showOrderForm, setShowOrderForm] = useState(false)
  const [createdOrder, setCreatedOrder] = useState(null)
  
  // Fetch products from ProductService
  useEffect(() => {
    loadProducts()
  }, [page])
  
  const loadProducts = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Educational Note: This calls ProductService API via our API layer
      // The JWT token is automatically added by axios interceptor
      const data = await fetchProducts(page, searchTerm)
      
      setProducts(data.results || data)
      
      // Handle pagination if available
      if (data.count) {
        setTotalPages(Math.ceil(data.count / 20))
      }
      
      setLoading(false)
    } catch (err) {
      console.error('Error fetching products:', err)
      setError(err.response?.data?.detail || 'Failed to load products')
      setLoading(false)
    }
  }
  
  // Handle search
  const handleSearch = (term) => {
    setSearchTerm(term)
    setPage(1)
    loadProducts()
  }
  
  // Add product to cart
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.id)
    
    if (existingItem) {
      // Increase quantity
      setCart(cart.map(item =>
        item.product_id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ))
    } else {
      // Add new item
      setCart([...cart, {
        product_id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1,
        max_quantity: product.inventory_count,
      }])
    }
  }
  
  // Remove from cart
  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.product_id !== productId))
  }
  
  // Update quantity in cart
  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId)
      return
    }
    
    setCart(cart.map(item =>
      item.product_id === productId
        ? { ...item, quantity: Math.min(newQuantity, item.max_quantity) }
        : item
    ))
  }
  
  // Calculate cart total
  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  
  return (
    <Container maxWidth="2xl" className="py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Products</h1>
        <ProductSearch onSearch={handleSearch} loading={loading} />
      </div>
      
      {/* Error message */}
      <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
      
      {/* Cart Summary (if items in cart) */}
      {cart.length > 0 && (
        <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Cart ({cart.length} {cart.length === 1 ? 'item' : 'items'})
            </h2>
            <div className="text-2xl font-bold text-blue-600">
              ${cartTotal.toFixed(2)}
            </div>
          </div>
          
          <div className="space-y-2 mb-4">
            {cart.map(item => (
              <div key={item.product_id} className="flex justify-between items-center bg-white p-3 rounded">
                <div className="flex-1">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-sm text-gray-600">${item.price} each</div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                    className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    -
                  </button>
                  <span className="w-8 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                    className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                    disabled={item.quantity >= item.max_quantity}
                  >
                    +
                  </button>
                  <Button
                    variant="danger"
                    onClick={() => removeFromCart(item.product_id)}
                    className="ml-2"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
          
          <Button
            variant="primary"
            onClick={() => setShowOrderForm(true)}
            className="w-full py-3 font-semibold"
          >
            Proceed to Checkout
          </Button>
        </div>
      )}
      
      {/* Order Form Modal */}
      {showOrderForm && (
        <OrderForm
          cart={cart}
          onSuccess={(order) => {
            setCreatedOrder(order)
            setShowOrderForm(false)
            setCart([]) // Clear cart after successful order
          }}
          onCancel={() => setShowOrderForm(false)}
        />
      )}
      
      {/* Order Success Modal */}
      {createdOrder && (
        <OrderSuccess
          order={createdOrder}
          onClose={() => setCreatedOrder(null)}
        />
      )}
      
      {/* Product Grid */}
      <ProductGrid
        products={products}
        loading={loading}
        onAddToCart={addToCart}
      />
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex justify-center gap-2">
          <Button
            variant="secondary"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="px-4 py-2 text-gray-700 flex items-center">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}
      
      {/* Educational Note */}
      <div className="mt-12 p-6 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-2">🎓 Educational Note</h3>
        <p className="text-gray-700">
          This page demonstrates fetching data from ProductService via REST API.
          The JWT token is automatically included in requests by the axios interceptor.
          Products are displayed in a responsive grid with search and pagination.
          The cart functionality prepares items for order creation through OrderService.
        </p>
      </div>
    </Container>
  )
}

export default Products
