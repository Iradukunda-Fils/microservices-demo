/**
 * ProductService API Module
 * 
 * Educational Note: This module handles all communication with the ProductService backend.
 * 
 * ProductService Responsibilities:
 * - Product catalog management
 * - Inventory tracking
 * - Product search and filtering
 * 
 * Why call ProductService directly?
 * When the frontend needs product data, it calls ProductService directly because:
 * 1. ProductService owns the product data
 * 2. No orchestration or cross-service logic is needed
 * 3. Direct calls are simpler and more efficient
 * 
 * Service Boundary: ProductService manages everything related to products and inventory.
 * It does NOT handle orders or users - those are separate services.
 */

import axiosInstance from '../utils/axios'

/**
 * Fetch paginated list of products.
 * 
 * @param {number} page - Page number (1-indexed)
 * @param {string} searchTerm - Optional search term for filtering
 * @returns {Promise<Object>} Paginated product list
 * 
 * Educational Note: This calls ProductService's product list endpoint.
 * The JWT token is automatically included by the axios interceptor.
 * ProductService verifies the token using UserService's public key
 * (loaded at startup via shared volume or HTTP request).
 * 
 * This demonstrates how services can verify JWTs independently without
 * calling UserService for every request - much more scalable!
 */
export async function fetchProducts(page = 1, searchTerm = '') {
  const params = { page }
  
  if (searchTerm) {
    params.search = searchTerm
  }
  
  const response = await axiosInstance.get('/api/products/', { params })
  return response.data
}

/**
 * Fetch a single product by ID.
 * 
 * @param {number} id - Product ID
 * @returns {Promise<Object>} Product details
 * 
 * Educational Note: This retrieves detailed information about a specific product.
 * Useful for product detail pages or when you need to refresh product data.
 */
export async function fetchProductById(id) {
  const response = await axiosInstance.get(`/api/products/${id}/`)
  return response.data
}

/**
 * Search products by name or description.
 * 
 * @param {string} query - Search query
 * @returns {Promise<Object>} Search results
 * 
 * Educational Note: This uses ProductService's search functionality.
 * The search is performed on the backend using database queries,
 * which is more efficient than filtering on the frontend.
 */
export async function searchProducts(query) {
  const response = await axiosInstance.get('/api/products/', {
    params: { search: query },
  })
  return response.data
}
