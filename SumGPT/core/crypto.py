import base64
import os
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class Crypto:
    def __init__(self, password: str, salt: Optional[bytes] = None):
        """Initialize Crypto class with password and optional salt."""
        self.password = password
        self.salt = salt if salt else os.urandom(16)  # Generate salt if not provided
        self.key = self._generate_key()

    def _generate_key(self) -> bytes:
        """Generate a symmetric key from the password using Scrypt KDF."""
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=2**14,  # CPU/memory cost factor
            r=8,  # Block size
            p=1,  # Parallelization factor
            backend=default_backend(),
        )
        key = kdf.derive(self.password.encode())
        return key

    def encrypt(self, data: str) -> bytes:
        """Encrypt data using AES GCM mode (authenticated encryption)."""
        nonce = os.urandom(12)  # 12-byte nonce for GCM mode
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        # Prepend the salt to the nonce, tag, and ciphertext for storage
        return self.salt + nonce + encryptor.tag + ciphertext

    def encrypt_b64(self, data: str) -> str:
        """Encrypt data and return as base64 encoded string."""
        encrypted_data = self.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data encrypted with AES GCM mode."""
        # Extract the salt, nonce, tag, and ciphertext
        salt = encrypted_data[:16]  # First 16 bytes are the salt
        nonce = encrypted_data[16:28]  # Next 12 bytes are the nonce
        tag = encrypted_data[28:44]  # Next 16 bytes are the GCM tag
        ciphertext = encrypted_data[44:]  # Rest is the ciphertext

        # Regenerate the key with the extracted salt
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
        key = kdf.derive(self.password.encode())

        # Initialize the cipher for decryption
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data.decode()
    
    def decrypt_b64(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data."""
        decoded_bytes = base64.b64decode(encrypted_data)
        return self.decrypt(decoded_bytes)
