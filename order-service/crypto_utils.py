"""
Professional-grade encryption utilities for microservices.

Educational Note: This module provides RSA 4096-bit asymmetric encryption
for inter-service communication and sensitive data protection.

Why Asymmetric Encryption?
- Public key can be shared freely
- Only private key holder can decrypt
- Perfect for distributed systems
- Industry standard for secure communication

Use Cases:
- Encrypting sensitive data in gRPC calls
- Protecting PII in logs
- Secure inter-service data transfer
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Professional-grade encryption manager using RSA 4096-bit.
    
    Educational Note: This class handles:
    1. Key pair generation (RSA 4096-bit)
    2. Encryption using public key
    3. Decryption using private key
    4. Key storage and loading
    
    Security Level: RSA 4096-bit provides 150+ years of protection
    against current cryptographic attacks.
    """
    
    @staticmethod
    def generate_key_pair() -> Tuple:
        """
        Generate RSA 4096-bit key pair.
        
        Educational Note:
        - public_exponent=65537: Standard value (Fermat number F4)
        - key_size=4096: Professional-grade security
        - Takes ~1 second to generate (one-time cost)
        
        Returns:
            Tuple of (private_key, public_key)
        """
        logger.info("Generating RSA 4096-bit key pair...")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # Professional-grade (150+ years security)
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        logger.info("✓ RSA key pair generated successfully")
        
        return private_key, public_key
    
    @staticmethod
    def save_private_key(private_key, filepath: str, password: bytes = None):
        """
        Save private key to file.
        
        Educational Note: In production, ALWAYS encrypt private keys
        with a password. For this demo, we use no encryption for simplicity.
        
        Args:
            private_key: RSA private key
            filepath: Path to save the key
            password: Optional password for encryption (use in production!)
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Serialize private key
        encryption_algorithm = serialization.NoEncryption()
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password)
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(pem)
        
        logger.info(f"✓ Private key saved to {filepath}")
    
    @staticmethod
    def save_public_key(public_key, filepath: str):
        """
        Save public key to file.
        
        Educational Note: Public keys can be shared freely.
        They're used for encryption, not decryption.
        
        Args:
            public_key: RSA public key
            filepath: Path to save the key
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Serialize public key
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(pem)
        
        logger.info(f"✓ Public key saved to {filepath}")
    
    @staticmethod
    def load_private_key(filepath: str, password: bytes = None):
        """
        Load private key from file.
        
        Args:
            filepath: Path to the private key file
            password: Optional password if key is encrypted
        
        Returns:
            RSA private key
        """
        with open(filepath, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password,
                backend=default_backend()
            )
        
        logger.info(f"✓ Private key loaded from {filepath}")
        return private_key
    
    @staticmethod
    def load_public_key(filepath: str):
        """
        Load public key from file.
        
        Args:
            filepath: Path to the public key file
        
        Returns:
            RSA public key
        """
        with open(filepath, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        
        logger.info(f"✓ Public key loaded from {filepath}")
        return public_key
    
    @staticmethod
    def encrypt(data: str, public_key) -> bytes:
        """
        Encrypt data using RSA public key.
        
        Educational Note: Uses OAEP padding with SHA-256.
        - OAEP: Optimal Asymmetric Encryption Padding
        - SHA-256: Secure hash algorithm
        - This is the recommended padding for RSA encryption
        
        Args:
            data: String data to encrypt
            public_key: RSA public key
        
        Returns:
            Encrypted data as bytes
        """
        encrypted = public_key.encrypt(
            data.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        logger.debug(f"✓ Data encrypted (size: {len(encrypted)} bytes)")
        return encrypted
    
    @staticmethod
    def decrypt(encrypted_data: bytes, private_key) -> str:
        """
        Decrypt data using RSA private key.
        
        Educational Note: Only the holder of the private key can decrypt.
        This is why asymmetric encryption is perfect for distributed systems.
        
        Args:
            encrypted_data: Encrypted bytes
            private_key: RSA private key
        
        Returns:
            Decrypted string
        """
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        logger.debug("✓ Data decrypted successfully")
        return decrypted.decode('utf-8')
    
    @staticmethod
    def encrypt_for_logging(data: str, public_key) -> str:
        """
        Encrypt data and return as base64 string for logging.
        
        Educational Note: Use this when you need to log sensitive data.
        The encrypted data can be safely logged and decrypted later if needed.
        
        Args:
            data: String data to encrypt
            public_key: RSA public key
        
        Returns:
            Base64-encoded encrypted data
        """
        import base64
        encrypted = EncryptionManager.encrypt(data, public_key)
        return base64.b64encode(encrypted).decode('utf-8')


# Educational Note: Example usage
if __name__ == '__main__':
    """
    Example usage of EncryptionManager.
    
    This demonstrates the complete encryption workflow:
    1. Generate key pair
    2. Encrypt data with public key
    3. Decrypt data with private key
    4. Verify round-trip works
    """
    
    print("=== RSA Encryption Demo ===\n")
    
    # Generate key pair
    print("1. Generating RSA 4096-bit key pair...")
    private_key, public_key = EncryptionManager.generate_key_pair()
    print("   ✓ Keys generated\n")
    
    # Original data
    original_data = "user_id:12345"
    print(f"2. Original data: {original_data}")
    
    # Encrypt
    print("3. Encrypting with public key...")
    encrypted = EncryptionManager.encrypt(original_data, public_key)
    print(f"   ✓ Encrypted (size: {len(encrypted)} bytes)")
    print(f"   ✓ Encrypted data: {encrypted[:50]}... (truncated)\n")
    
    # Decrypt
    print("4. Decrypting with private key...")
    decrypted = EncryptionManager.decrypt(encrypted, private_key)
    print(f"   ✓ Decrypted: {decrypted}\n")
    
    # Verify
    print("5. Verification:")
    if original_data == decrypted:
        print("   ✓ SUCCESS: Round-trip encryption works!")
        print("   ✓ Original == Decrypted")
    else:
        print("   ✗ FAILED: Data mismatch")
    
    print("\n=== Demo Complete ===")
    print("\nEducational Notes:")
    print("- Public key can be shared freely (used for encryption)")
    print("- Private key must be kept secret (used for decryption)")
    print("- RSA 4096-bit provides 150+ years of security")
    print("- Perfect for encrypting sensitive data in microservices")
