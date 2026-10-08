from .paste.crypto import encrypt

import argparse, sys, urllib.request, json

def cmd_put(args):
    plaintext = sys.stdin.read() if args.text == "-" else args.text
    iv, salt, ct = encrypt(plaintext, args.password)
    body = json.dumps({"ciphertext": ct, "iv": iv, "salt": salt,
                       "expiry": args.expiry, "burn": args.burn}).encode()
    req = urllib.request.Request("http://127.0.0.1:5000/api/pastes", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        print(r.read().decode())

def main():
    p = argparse.ArgumentParser(prog="pb")
    sub = p.add_subparsers(dest="cmd")
    put = sub.add_parser("put"); put.add_argument("text")
    put.add_argument("--password", required=True)
    put.add_argument("--expiry", default="1d"); put.add_argument("--burn", action="store_true")
    args = p.parse_args()
    if args.cmd == "put":
        return cmd_put(args)
    p.print_help()
    return 1
