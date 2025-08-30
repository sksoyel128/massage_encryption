# encryption.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
from typing import Tuple

# Path to persistent global key (backwards compatible)
KEY_FILE = "data/aes_key.bin"

class AESCipher:
    """
    AES helper. If `key` passed to constructor is None, loads/creates persistent key in KEY_FILE.
    If `key` is provided (bytes), that key is used (useful for per-session keys).
    Methods:
        encrypt(raw: str) -> (ciphertext_bytes, iv_bytes)
        decrypt(ciphertext: bytes, iv: bytes) -> plaintext_str
    """
    def __init__(self, key: bytes = None):
        if key is not None:
            self.key = key
        else:
            self.key = self._load_or_create_key()

        if len(self.key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24 or 32 bytes long.")

    def _load_or_create_key(self) -> bytes:
        os.makedirs("data", exist_ok=True)
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        key = get_random_bytes(32)  # AES-256
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

    def encrypt(self, raw: str) -> Tuple[bytes, bytes]:
        """
        Encrypt `raw` string and return (ciphertext_bytes, iv_bytes).
        Uses AES-CBC with PKCS7 padding.
        """
        raw_bytes = raw.encode("utf-8")
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(raw_bytes, AES.block_size))
        return ct, iv

    def decrypt(self, ciphertext: bytes, iv: bytes) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return pt.decode("utf-8")
