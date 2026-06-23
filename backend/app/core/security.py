"""
Security utilities for passwords and stored SMTP secrets.
"""
from passlib.context import CryptContext
import base64
import hashlib

from app.core.config import settings

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
        
    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# Optional: Generate a random password for testing
def generate_temp_password(length: int = 16) -> str:
    """
    Generate a random temporary password
    
    Args:
        length: Password length (default: 16)
        
    Returns:
        Random password string
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def _secret_key_stream(length: int) -> bytes:
    """Build a deterministic key stream from SECRET_KEY for local secret storage."""
    seed = settings.SECRET_KEY.encode("utf-8")
    stream = b""
    counter = 0
    while len(stream) < length:
        stream += hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        counter += 1
    return stream[:length]


def encrypt_secret(secret: str) -> str:
    """
    Reversibly encode an SMTP secret for storage.

    SMTP passwords must be recoverable for server login. This keeps credentials
    out of API responses, but production deployments should use a real KMS or
    strong authenticated encryption.
    """
    raw = secret.encode("utf-8")
    key = _secret_key_stream(len(raw))
    encrypted = bytes(value ^ key[index] for index, value in enumerate(raw))
    return "enc:" + base64.urlsafe_b64encode(encrypted).decode("ascii")


def decrypt_secret(stored_secret: str) -> str:
    """Decode a stored SMTP secret. Plain values are accepted for legacy rows."""
    if not stored_secret.startswith("enc:"):
        return stored_secret

    encrypted = base64.urlsafe_b64decode(stored_secret[4:].encode("ascii"))
    key = _secret_key_stream(len(encrypted))
    raw = bytes(value ^ key[index] for index, value in enumerate(encrypted))
    return raw.decode("utf-8")


if __name__ == "__main__":
    # Test the password hashing
    test_password = "my_secure_password_123"
    
    print("Password Hashing Test")
    print("=" * 50)
    print(f"Original password: {test_password}")
    
    # Hash the password
    hashed = hash_password(test_password)
    print(f"Hashed password: {hashed}")
    
    # Verify correct password
    is_valid = verify_password(test_password, hashed)
    print(f"Verification (correct): {is_valid}")
    
    # Verify wrong password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"Verification (wrong): {is_invalid}")
    
    # Generate random password
    random_pass = generate_temp_password()
    print(f"\nRandom password: {random_pass}")
