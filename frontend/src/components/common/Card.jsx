/**
 * Reusable Card component for consistent container styling.
 * 
 * Educational Note: Cards are a common UI pattern for grouping related content.
 * This component provides consistent styling across the application.
 */

/**
 * Card component with optional hover effect.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Card content
 * @param {boolean} props.hover - Enable hover effect
 * @param {string} props.className - Additional CSS classes
 */
function Card({ children, hover = false, className = '' }) {
  const hoverStyles = hover ? 'hover:shadow-lg transition-shadow' : ''
  
  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${hoverStyles} ${className}`}>
      {children}
    </div>
  )
}

export default Card
