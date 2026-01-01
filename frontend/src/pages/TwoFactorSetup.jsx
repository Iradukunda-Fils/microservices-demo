/**
 * Two-Factor Authentication setup page.
 * 
 * Educational Note: This component demonstrates TOTP-based 2FA setup:
 * 1. Generate QR code for authenticator apps (Google Authenticator, Authy)
 * 2. Display backup tokens for account recovery
 * 3. Verify setup with a 6-digit code
 * 4. Allow disabling 2FA with password confirmation
 * 
 * TOTP (Time-based One-Time Password) is more secure than SMS-based 2FA
 * because it doesn't rely on phone networks which can be intercepted.
 */

import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { QRCodeSVG } from 'qrcode.react'
import Container from '../components/layout/Container'
import Button from '../components/common/Button'
import ErrorMessage from '../components/common/ErrorMessage'

function TwoFactorSetup() {
  const { setup2FA, verify2FASetup, disable2FA, check2FAStatus } = useAuth()
  
  const [is2FAEnabled, setIs2FAEnabled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [setupData, setSetupData] = useState(null)
  const [verificationCode, setVerificationCode] = useState('')
  const [disablePassword, setDisablePassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showBackupTokens, setShowBackupTokens] = useState(false)
  
  // Check 2FA status on mount
  useEffect(() => {
    checkStatus()
  }, [])
  
  const checkStatus = async () => {
    setLoading(true)
    const result = await check2FAStatus()
    
    if (result.success) {
      setIs2FAEnabled(result.data.enabled)
    }
    
    setLoading(false)
  }
  
  const handleSetup = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    
    const result = await setup2FA()
    
    if (result.success) {
      setSetupData(result.data)
      setSuccess('2FA setup initiated. Scan the QR code with your authenticator app.')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }
  
  const handleVerifySetup = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    
    const result = await verify2FASetup(verificationCode, setupData?.device_id)
    
    if (result.success) {
      setSuccess('2FA enabled successfully! Save your backup tokens in a safe place.')
      setIs2FAEnabled(true)
      setShowBackupTokens(true)
      setVerificationCode('')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }
  
  const handleDisable = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    
    const result = await disable2FA(disablePassword)
    
    if (result.success) {
      setSuccess('2FA disabled successfully.')
      setIs2FAEnabled(false)
      setSetupData(null)
      setDisablePassword('')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }
  
  const downloadBackupTokens = async () => {
    if (!setupData?.backup_tokens) return
    
    try {
      setLoading(true)
      
      // Import the API function
      const { downloadBackupTokens: downloadAPI } = await import('../api/userService')
      
      // Call backend to generate formatted file
      const result = await downloadAPI(setupData.backup_tokens)
      
      // Decode base64 content
      const content = atob(result.content)
      
      // Create blob and download
      const blob = new Blob([content], { type: result.mime_type })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = result.filename
      a.click()
      URL.revokeObjectURL(url)
      
      setSuccess('Backup tokens downloaded successfully!')
    } catch (error) {
      console.error('Download error:', error)
      setError('Failed to download backup tokens. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  if (loading && !setupData) {
    return (
      <Container maxWidth="lg" className="py-12">
        <div className="flex items-center justify-center">
          <div className="text-xl text-gray-600">Loading 2FA status...</div>
        </div>
      </Container>
    )
  }
  
  return (
    <Container maxWidth="lg" className="py-12">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
          Two-Factor Authentication
        </h2>
        
        <div className="mb-6 p-4 bg-gray-50 rounded-lg text-center">
          <p className="text-gray-700">
            <strong>Status:</strong>{' '}
            {is2FAEnabled ? (
              <span className="text-green-600 font-semibold">✓ Enabled</span>
            ) : (
              <span className="text-red-600 font-semibold">✗ Disabled</span>
            )}
          </p>
        </div>
        
        <ErrorMessage message={error} onDismiss={() => setError('')} className="mb-6" />
        
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}
        
        {!is2FAEnabled && !setupData && (
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Enable Two-Factor Authentication
            </h3>
            <p className="text-gray-600 mb-6">
              Add an extra layer of security to your account. You'll need to enter
              a code from your authenticator app when you log in.
            </p>
            
            <div className="mb-6 p-6 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">Benefits of 2FA:</h4>
              <ul className="space-y-2 text-gray-700">
                <li>🔒 Protects your account even if your password is compromised</li>
                <li>📱 Works with Google Authenticator, Authy, and other TOTP apps</li>
                <li>🔑 Backup tokens for account recovery</li>
                <li>🚫 More secure than SMS-based 2FA</li>
              </ul>
            </div>
            
            <Button
              onClick={handleSetup}
              variant="primary"
              loading={loading}
            >
              Enable 2FA
            </Button>
          </div>
        )}
        
        {setupData && !is2FAEnabled && (
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Step 1: Scan QR Code
            </h3>
            <p className="text-gray-600 mb-6">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </p>
            
            <div className="flex justify-center p-8 bg-white rounded-lg mb-6">
              {setupData.qr_code ? (
                <img 
                  src={setupData.qr_code} 
                  alt="2FA QR Code" 
                  className="w-64 h-64"
                />
              ) : (
                <QRCodeSVG
                  value={setupData.qr_code_url || ''}
                  size={256}
                  level="H"
                  includeMargin={true}
                />
              )}
            </div>
            
            <div className="text-center mb-8">
              <p className="text-gray-700 mb-2"><strong>Can't scan?</strong> Enter this code manually:</p>
              <code className="block mt-2 p-4 bg-gray-100 rounded-lg text-lg tracking-widest break-all">
                {setupData.secret_key || setupData.secret}
              </code>
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Step 2: Verify Setup
            </h3>
            <p className="text-gray-600 mb-6">
              Enter the 6-digit code from your authenticator app to verify the setup.
            </p>
            
            <form onSubmit={handleVerifySetup} className="max-w-md mx-auto space-y-6">
              <div>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength="6"
                  pattern="[0-9]{6}"
                  required
                  autoComplete="off"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-2xl tracking-widest font-mono"
                />
              </div>
              
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                disabled={verificationCode.length !== 6}
                className="w-full"
              >
                Verify and Enable
              </Button>
            </form>
            
            {setupData.backup_tokens && (
              <div className="mt-8 p-6 bg-yellow-50 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Step 3: Save Backup Tokens
                </h3>
                <div className="mb-4 p-4 bg-yellow-100 border border-yellow-300 rounded-lg text-yellow-800">
                  <strong>⚠️ Important:</strong> Save these backup tokens in a safe place!
                  Each token can only be used once. You'll need them if you lose access
                  to your authenticator app.
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
                  {setupData.backup_tokens.map((token, index) => (
                    <div key={index} className="p-3 bg-white border border-gray-300 rounded-lg text-center">
                      <code className="text-sm tracking-wider">{token}</code>
                    </div>
                  ))}
                </div>
                
                <Button
                  onClick={downloadBackupTokens}
                  variant="secondary"
                >
                  📥 Download Backup Tokens
                </Button>
              </div>
            )}
          </div>
        )}
        
        {is2FAEnabled && (
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Manage Backup Tokens
            </h3>
            <p className="text-gray-600 mb-6">
              Regenerate your backup tokens if you've used them all or suspect they've been compromised.
            </p>
            
            <Button
              onClick={async () => {
                setError('')
                setSuccess('')
                setLoading(true)
                
                // Prompt for password
                const password = prompt('Enter your password to regenerate backup tokens:')
                if (!password) {
                  setLoading(false)
                  return
                }
                
                try {
                  const { regenerateBackupTokens } = await import('../api/userService')
                  const result = await regenerateBackupTokens(password)
                  
                  // Store new tokens for download
                  setSetupData({ backup_tokens: result.backup_tokens })
                  setSuccess('New backup tokens generated! Download them now.')
                } catch (err) {
                  setError(err.response?.data?.error || 'Failed to regenerate tokens')
                } finally {
                  setLoading(false)
                }
              }}
              variant="secondary"
              loading={loading}
            >
              🔄 Regenerate Backup Tokens
            </Button>
            
            {setupData?.backup_tokens && (
              <div className="mt-6 p-6 bg-yellow-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">New Backup Tokens Generated</h4>
                <div className="mb-4 p-4 bg-yellow-100 border border-yellow-300 rounded-lg text-yellow-800">
                  <strong>⚠️ Important:</strong> Download these tokens now! Old tokens are now invalid.
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                  {setupData.backup_tokens.map((token, index) => (
                    <div key={index} className="p-3 bg-white border border-gray-300 rounded-lg text-center">
                      <code className="text-sm tracking-wider">{token}</code>
                    </div>
                  ))}
                </div>
                
                <Button
                  onClick={downloadBackupTokens}
                  variant="primary"
                >
                  📥 Download New Backup Tokens
                </Button>
              </div>
            )}
          </div>
        )}
        
        {is2FAEnabled && (
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Disable Two-Factor Authentication
            </h3>
            <p className="text-gray-600 mb-6">
              To disable 2FA, enter your password for confirmation.
            </p>
            
            <form onSubmit={handleDisable} className="max-w-md mx-auto space-y-6">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  autoComplete="current-password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <Button
                type="submit"
                variant="secondary"
                loading={loading}
                className="w-full"
              >
                Disable 2FA
              </Button>
            </form>
          </div>
        )}
        
        <div className="p-6 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-3">Need Help?</h4>
          <ul className="space-y-2 text-gray-700">
            <li>
              <strong>Lost your phone?</strong> Use one of your backup tokens to log in.
            </li>
            <li>
              <strong>Authenticator app not working?</strong> Make sure your device's
              time is synchronized correctly.
            </li>
            <li>
              <strong>Can't access backup tokens?</strong> Contact support for account
              recovery.
            </li>
          </ul>
        </div>
      </div>
    </Container>
  )
}

export default TwoFactorSetup
