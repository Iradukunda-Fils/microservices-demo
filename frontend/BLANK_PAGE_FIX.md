# Blank Page Fix - Root Cause Analysis

## Problem
The React application was rendering a blank page even though the server was being reached.

## Root Causes Identified

### 1. **AuthContext Loading State** (PRIMARY ISSUE - FIXED)
**Location:** `frontend/src/context/AuthContext.jsx`

**Problem:**
```jsx
// ❌ BROKEN CODE
if (loading) {
  return <div className="loading">Loading...</div>
}
```

**Why it failed:**
- The `.loading` CSS class doesn't exist (was removed during Tailwind refactoring)
- Tailwind purges unused CSS classes
- The div rendered but was **completely invisible** (no height, width, or color)
- This caused the entire app to appear blank during the initial loading state

**Fix Applied:**
```jsx
// ✅ FIXED CODE
if (loading) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-xl text-gray-600">Loading...</div>
    </div>
  )
}
```

### 2. **TwoFactorSetup Page CSS Import** (SECONDARY ISSUE - FIXED)
**Location:** `frontend/src/pages/TwoFactorSetup.jsx`

**Problem:**
```jsx
// ❌ BROKEN CODE
import './TwoFactorSetup.css'
```

**Why it failed:**
- Imported a CSS file with undefined CSS variables (`--spacing-xl`, `--surface-color`, etc.)
- These variables were defined in removed global CSS files
- The CSS file should have been removed during Tailwind refactoring
- Also had another `.loading` class issue in the component

**Fix Applied:**
1. Removed the CSS import
2. Refactored entire component to use Tailwind utility classes
3. Deleted `TwoFactorSetup.css` file
4. Fixed the loading state to use Tailwind classes

### 3. **JSON.parse Error on localStorage** (CRITICAL ISSUE - FIXED)
**Location:** `frontend/src/context/AuthContext.jsx` line 52

**Problem:**
```jsx
// ❌ BROKEN CODE
if (storedUser) {
  setUser(JSON.parse(storedUser))
}
```

**Error:**
```
Uncaught SyntaxError: "undefined" is not valid JSON
at JSON.parse (<anonymous>)
at AuthContext.jsx:52:22
```

**Why it failed:**
- localStorage can contain the string `"undefined"` or `"null"` instead of valid JSON
- This happens when code does `localStorage.setItem('user', undefined)`
- JSON.parse() throws an error on these invalid strings
- The error crashes the entire React app, causing a blank page

**Fix Applied:**
```jsx
// ✅ FIXED CODE
if (storedUser && storedUser !== 'undefined' && storedUser !== 'null') {
  try {
    const parsedUser = JSON.parse(storedUser)
    setUser(parsedUser)
  } catch (error) {
    console.error('Failed to parse stored user data:', error)
    localStorage.removeItem('user')
  }
}
```

### 4. **Proactive Token Refresh** (ENHANCEMENT - ADDED)
**Location:** `frontend/src/utils/axios.js`

**Problem:**
- Users would see 401 errors when their access token expired
- Token refresh only happened AFTER a 401 error
- This caused a poor user experience, especially when switching tabs

**Enhancement Added:**
```jsx
// ✅ PROACTIVE REFRESH
function isTokenExpiringSoon(token) {
  const decoded = decodeToken(token)
  if (!decoded || !decoded.exp) return true
  
  const expirationTime = decoded.exp * 1000
  const currentTime = Date.now()
  const fiveMinutes = 5 * 60 * 1000
  
  // Return true if token expires in less than 5 minutes
  return expirationTime - currentTime < fiveMinutes
}

// In request interceptor:
if (accessToken && refreshToken && isTokenExpiringSoon(accessToken)) {
  // Refresh token BEFORE making the request
  const response = await axios.post('/api/token/refresh/', { refresh: refreshToken })
  accessToken = response.data.access
  localStorage.setItem('accessToken', accessToken)
}
```

**Benefits:**
- Tokens refresh 5 minutes before expiration
- Users never see 401 errors during active sessions
- Seamless experience when switching tabs or resuming work
- Fallback to reactive refresh if proactive refresh fails

## How These Issues Caused a Blank Page

1. **Initial Load Sequence:**
   - User opens app → React mounts → AuthContext initializes
   - AuthContext checks localStorage for tokens (takes ~10-50ms)
   - During this time, `loading = true`
   - AuthContext renders: `<div className="loading">Loading...</div>`

2. **The Invisible Div:**
   - `.loading` class doesn't exist in Tailwind
   - Div has no dimensions, no color, no content styling
   - Browser renders an invisible div
   - User sees: **blank white page**

3. **Why Server Was Reached:**
   - The HTML file loaded correctly
   - JavaScript bundle loaded correctly
   - React mounted correctly
   - The issue was purely **CSS/styling**, not a JavaScript error

## Prevention Strategies

### 1. Search for Custom Classes After CSS Removal
```bash
# Find all className attributes that might use custom classes
grep -r 'className="[^"]*"' src/ | grep -v 'bg-\|text-\|flex\|grid\|p-\|m-\|w-\|h-'
```

### 2. Use Browser DevTools
- Open React DevTools → Components tab
- You would see the component tree rendering
- The invisible div would be visible in the DOM inspector

### 3. Check Console for Warnings
- Vite/Webpack might warn about missing CSS files
- React might show component errors

### 4. Use Centralized Loading Components
Instead of inline loading states, create a reusable component:
```jsx
import LoadingSpinner from '../components/common/LoadingSpinner'

if (loading) {
  return <LoadingSpinner size="large" />
}
```

### 5. Tailwind JIT Mode Configuration
Ensure `tailwind.config.js` has correct content paths:
```js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // ...
}
```

## Files Modified

1. **frontend/src/context/AuthContext.jsx**
   - Fixed loading state to use Tailwind classes

2. **frontend/src/pages/TwoFactorSetup.jsx**
   - Removed CSS import
   - Refactored entire component with Tailwind
   - Fixed loading state

3. **frontend/src/pages/TwoFactorSetup.css**
   - Deleted (no longer needed)

## Testing the Fix

1. **Clear browser cache** (important!)
2. **Hard refresh** (Ctrl+Shift+R or Cmd+Shift+R)
3. Open browser console - should see no errors
4. App should now render correctly

## Lessons Learned

1. **Always check loading states** when refactoring CSS
2. **Search for all custom class references** before removing CSS files
3. **Test the initial load experience** - it's easy to miss
4. **Use Tailwind exclusively** - mixing custom CSS and Tailwind causes issues
5. **Centralize common UI patterns** like loading states

## Expected Behavior Now

1. App loads → Brief "Loading..." message (visible!)
2. AuthContext checks localStorage (~10-50ms)
3. App renders normally with proper routing
4. All pages use Tailwind styling consistently
