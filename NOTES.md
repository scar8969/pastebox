== curl ==
# POST /api/pastes  {"ciphertext":"…","iv":"…","salt":"…","lang":"python","expiry":"1d","burn":false}
# GET  /p/8f3k2a
# DELETE /p/8f3k2a
# CLI: echo "secret" | pb put - --password mypass --expiry 1h

== session plan ==
# Session 1: crypto (PBKDF2 + AES-GCM roundtrip) → tests
# Session 2: store (expiry/burn/sweep) + api → tests
# Session 3: web (client-side decrypt) + cli → screenshots → README → CI/Docker/Pages → tag
