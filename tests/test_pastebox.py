"""B4 pastebin — tests. Run: pytest test_pastebox.py"""

import pytest


def test_encrypt_decrypt_roundtrip():
    from pastebin.paste.crypto import decrypt, encrypt

    iv, salt, ct = encrypt("secret message", "mypassword")
    assert decrypt(ct, iv, salt, "mypassword") == "secret message"


def test_wrong_password():
    from pastebin.paste.crypto import decrypt, encrypt

    iv, salt, ct = encrypt("secret", "right")
    with pytest.raises(ValueError):
        decrypt(ct, iv, salt, "wrong")


def test_iv_salt_unique():
    from pastebin.paste.crypto import encrypt

    iv1, salt1, ct1 = encrypt("same", "pw")
    iv2, salt2, ct2 = encrypt("same", "pw")
    assert ct1 != ct2  # random IV/salt → different ciphertext


def test_expiry_map():
    from pastebin.paste.store import _EXPIRY

    assert _EXPIRY["1d"] == 86400
    assert _EXPIRY["7d"] == 7 * 86400
