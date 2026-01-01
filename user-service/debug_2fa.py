#!/usr/bin/env python
"""
2FA Diagnostic Script
Run with: docker-compose exec user-service python debug_2fa.py
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()

from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp

print("=" * 60)
print("2FA DIAGNOSTIC REPORT")
print("=" * 60)

# Get first user
user = User.objects.first()
if not user:
    print("❌ No users found")
    exit(1)

print(f"\n✅ User: {user.username}")

# Get device
device = TOTPDevice.objects.filter(user=user).first()
if not device:
    print("❌ No TOTP device found")
    exit(1)

print(f"✅ Device found: {device.name}")
print(f"   - Confirmed: {device.confirmed}")
print(f"   - Tolerance: {device.tolerance}")
print(f"   - Digits: {device.digits}")
print(f"   - Step: {device.step}")
print(f"   - Drift: {device.drift}")

# Generate current codes
print(f"\n📱 TOTP Configuration:")
print(f"   - Secret (first 8 chars): {device.key[:8]}...")
print(f"   - Algorithm: SHA1")
print(f"   - Period: {device.step} seconds")
print(f"   - Digits: {device.digits}")

# Get current time
current_time = int(time.time())
print(f"\n🕐 Time Information:")
print(f"   - Current Unix timestamp: {current_time}")
print(f"   - Current time window: {current_time // device.step}")

# Generate codes using device's token method
print(f"\n🔢 Valid TOTP Codes (with tolerance={device.tolerance}):")
for drift_offset in range(-device.tolerance, device.tolerance + 1):
    code = totp(device.key, step=device.step, t0=device.t0, digits=device.digits, drift=drift_offset)
    marker = "👉 CURRENT" if drift_offset == 0 else f"   (drift {drift_offset:+d})"
    print(f"   {code:06d} {marker}")

# Test verification
print(f"\n🧪 Testing device.verify_token():")
current_code = totp(device.key, step=device.step, t0=device.t0, digits=device.digits, drift=0)
print(f"   - Current code: {current_code:06d}")
result = device.verify_token(str(current_code).zfill(6))
print(f"   - Verification result: {result}")

if not result:
    print("\n❌ VERIFICATION FAILED!")
    print("   Possible causes:")
    print("   1. Time drift between server and authenticator app")
    print("   2. Device not using correct parameters")
    print("   3. Secret key mismatch")
    
    # Try manual verification
    print("\n   Trying manual verification with different drifts...")
    for drift_offset in range(-2, 3):
        code = totp(device.key, step=device.step, t0=device.t0, digits=device.digits, drift=drift_offset)
        manual_result = device.verify_token(str(code).zfill(6))
        print(f"   - Code {code:06d} (drift {drift_offset:+d}): {manual_result}")

print("\n" + "=" * 60)
print("END OF DIAGNOSTIC REPORT")
print("=" * 60)
