/**
 * OrderService API Module
 * 
 * Educational Note: This module handles all communication with the OrderService backend.
 * 
 * OrderService Responsibilities:
 * - Order creation and management
 * - Cross-service orchestration
 * - Order validation (user exists, products exist, inventory available)
 * 
 * Why call OrderService instead of calling UserService and ProductService directly?
 * 
 * This is a KEY microservices pattern called "Service Orchestration":
 * 
 * ❌ WRONG APPROACH (Frontend orchestration):
 *    Frontend → UserService (validate user)
 *    Frontend → ProductService (validate products)
 *    Frontend → ProductService (check inventory)
 *    Frontend → OrderService (create order)
 * 
 * ✅ CORRECT APPROACH (Backend orchestration):
 *    Frontend → OrderService (create order)
 *    OrderService → UserService (validate user via gRPC)
 *    OrderService → ProductService (validate products via gRPC)
 *    OrderService → ProductService (check inventory via gRPC)
 *    OrderService → Database (create order)
 * 
 * Why is backend orchestration better?
 * 1. Single API call from frontend (simpler, faster)
 * 2. Atomic transaction - all validations happen together
 * 3. Business logic stays on backend (easier to maintain)
 * 4. Uses fast gRPC for internal communication (7-10x faster than REST)
 * 5. Retry logic and circuit breaker patterns on backend
 * 6. Frontend doesn't need to know about service dependencies
 * 
 * Service Boundary: OrderService orchestrates order creation by coordinating
 * with UserService and ProductService, but it owns the order data.
 * 
 * Security: All endpoints use JWT authentication. User ID comes from the
 * JWT token, not from client input. This prevents users from accessing or
 * creating orders for other users.
 */

import axiosInstance from '../utils/axios'

/**
 * Create a new order.
 * 
 * @param {Object} orderData - Order data
 * @param {Array} orderData.items - Array of order items
 * @param {number} orderData.items[].product_id - Product ID
 * @param {number} orderData.items[].quantity - Quantity
 * @returns {Promise<Object>} Created order with items
 * 
 * Educational Note: This is where the magic happens!
 * 
 * When you call this endpoint, OrderService performs these steps:
 * 
 * 1. EXTRACT USER ID from JWT token (secure - can't be spoofed)
 * 
 * 2. VALIDATE USER (via gRPC to UserService)
 *    - Checks if user_id exists
 *    - Uses gRPC for fast internal communication
 *    - Includes retry logic with exponential backoff
 * 
 * 3. VALIDATE PRODUCTS (via gRPC to ProductService)
 *    - Checks if all product_ids exist
 *    - Retrieves current prices
 *    - Uses gRPC for fast internal communication
 * 
 * 4. CHECK INVENTORY (via gRPC to ProductService)
 *    - Verifies sufficient inventory for each product
 *    - Prevents overselling
 * 
 * 5. CREATE ORDER (in OrderService database)
 *    - Stores user_id encrypted with AES-256
 *    - Stores order status (pending)
 *    - Calculates total amount
 * 
 * 6. CREATE ORDER ITEMS (in OrderService database)
 *    - Stores product_id, quantity, and price_at_purchase
 *    - Price snapshot prevents issues if product price changes later
 * 
 * Error Handling:
 * - 400: Validation failed (user not found, product not found, insufficient inventory)
 * - 401: Authentication required (no JWT token or invalid token)
 * - 503: Service unavailable (circuit breaker open, gRPC error)
 * - 500: Internal server error
 * 
 * Resilience Patterns:
 * - Retry logic: Automatically retries failed gRPC calls (up to 5 times)
 * - Exponential backoff: Waits longer between each retry (1s, 2s, 4s, 8s, 16s)
 * - Circuit breaker: Stops calling failing services temporarily to prevent cascading failures
 */
export async function createOrder(orderData) {
  const response = await axiosInstance.post('/api/orders/', orderData)
  return response.data
}

/**
 * Fetch all orders for the authenticated user.
 * 
 * @returns {Promise<Object>} List of orders with items
 * 
 * Educational Note: This retrieves order history for the authenticated user.
 * The user_id is automatically extracted from the JWT token on the backend.
 * Users can only see their own orders (enforced by backend).
 * 
 * Security:
 * - JWT token required (sent automatically by axios interceptor)
 * - Backend filters orders by user_id from token
 * - Users cannot access other users' orders
 */
export async function fetchUserOrders() {
  const response = await axiosInstance.get('/api/orders/')
  return response.data
}

/**
 * Fetch a single order by ID.
 * 
 * @param {number} id - Order ID
 * @returns {Promise<Object>} Order details with items
 * 
 * Educational Note: This retrieves detailed information about a specific order.
 * Includes all order items with product_id, quantity, and price_at_purchase.
 * 
 * Security:
 * - JWT token required
 * - Backend verifies the order belongs to the authenticated user
 * - Returns 404 if order doesn't exist or doesn't belong to user
 */
export async function fetchOrderById(id) {
  const response = await axiosInstance.get(`/api/orders/${id}/`)
  return response.data
}
