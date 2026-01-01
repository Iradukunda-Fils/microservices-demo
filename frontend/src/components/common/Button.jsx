/**
 * Reusable Button component with consistent styling.
 * 
 * Educational Note: Creating reusable components like this promotes:
 * - Consistent UI across the application
 * - Easier maintenance (change once, update everywhere)
 * - Better accessibility (centralized ARIA attributes)
 */

/**
 * Button component with multiple variants.
 * 
 * @param {Object} props
 * @param {string} props.variant - Button style variant: 'primary', 'secondary', 'danger'
 * @param {boolean} props.loading - Show loading spinner
 * @param {boolean} props.disabled - Disable button
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Button content
 * @param {Function} props.onClick - Click handler
 * @param {string} props.type - Button type: 'button', 'submit', 'reset'
 */
function Button({
  variant = 'primary',
  loading = false,
  disabled = false,
  className = '',
  children,
  onClick,
  type = 'button',
  ...props
}) {
  // Base styles for all buttons
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  // Variant-specific styles
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  }
  
  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className}`
  
  return (
    <button
      type={type}
      className={combinedClassName}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  )
}

export default Button
