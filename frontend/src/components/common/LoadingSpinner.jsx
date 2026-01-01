/**
 * Reusable LoadingSpinner component.
 * 
 * Educational Note: A simple, reusable loading indicator
 * that can be used throughout the application.
 */

/**
 * LoadingSpinner component with size variants.
 * 
 * @param {Object} props
 * @param {string} props.size - Spinner size: 'small', 'medium', 'large'
 * @param {string} props.className - Additional CSS classes
 */
function LoadingSpinner({ size = 'medium', className = '' }) {
  const sizeStyles = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12',
  }
  
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <svg
        className={`animate-spin text-blue-600 ${sizeStyles[size]}`}
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
    </div>
  )
}

export default LoadingSpinner
