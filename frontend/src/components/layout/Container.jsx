/**
 * Container component for consistent page layout.
 * 
 * Educational Note: A container component provides consistent
 * max-width and padding across all pages, ensuring a cohesive layout.
 */

/**
 * Container component with responsive padding.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Container content
 * @param {string} props.maxWidth - Max width class: 'sm', 'md', 'lg', 'xl', '2xl', 'full'
 * @param {string} props.className - Additional CSS classes
 */
function Container({ children, maxWidth = 'xl', className = '' }) {
  const maxWidthStyles = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    '2xl': 'max-w-screen-2xl',
    full: 'max-w-full',
  }
  
  return (
    <div className={`${maxWidthStyles[maxWidth]} mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  )
}

export default Container
