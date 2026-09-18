"""
Encryption utilities for storing sensitive credentials
Uses Fernet (symmetric encryption) from cryptography library
"""

from cryptography.fernet import Fernet
import os
import base64

# Get encryption key from environment
# In production, this should be stored securely (e.g., AWS Secrets Manager)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Generate a key for development (DO NOT use in production)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️  WARNING: Generated temporary encryption key. Set ENCRYPTION_KEY in .env for production!")
    print(f"ENCRYPTION_KEY={ENCRYPTION_KEY}")

# Initialize cipher
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_credential(value: str) -> str:
    """
    Encrypt a credential value
    
    Args:
        value: Plain text credential
    
    Returns:
        Encrypted credential as base64 string
    """
    if not value:
        return ""
    
    encrypted = cipher.encrypt(value.encode())
    return encrypted.decode()


def decrypt_credential(encrypted_value: str) -> str:
    """
    Decrypt a credential value
    
    Args:
        encrypted_value: Encrypted credential as base64 string
    
    Returns:
        Decrypted plain text credential
    
    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    if not encrypted_value:
        return ""
    
    decrypted = cipher.decrypt(encrypted_value.encode())
    return decrypted.decode()


# Example usage
if __name__ == "__main__":
    # Test encryption/decryption
    original = "my_secret_password"
    encrypted = encrypt_credential(original)
    decrypted = decrypt_credential(encrypted)
    
    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
