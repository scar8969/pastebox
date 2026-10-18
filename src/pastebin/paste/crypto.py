import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=_ITERS)
    return kdf.derive(password.encode())


def encrypt(plaintext, password):
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(password, salt)
    ct = AESGCM(key).encrypt(iv, plaintext.encode(), None)
    return (
        base64.b64encode(iv).decode(),
        base64.b64encode(salt).decode(),
        base64.b64encode(ct).decode(),
    )


def decrypt(ciphertext_b64, iv_b64, salt_b64, password):
    try:
        key = derive_key(password, base64.b64decode(salt_b64))
        pt = AESGCM(key).decrypt(base64.b64decode(iv_b64), base64.b64decode(ciphertext_b64), None)
        return pt.decode()
    except Exception:
        raise ValueError("wrong password or corrupted paste")


_ITERS = 100_000
