#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""new_RC4 writeup.

RC4 is symmetric, so decrypting is the same operation as encrypting.
We just run the extracted key stream over the embedded ciphertext.
"""

import subprocess
import sys

KEY = b"so_love_this"
CIPHER = bytes.fromhex("64adfa8d80f7f0bbad3ab03d9d1c3c9b30a78f0011e7ffdc2dd4")


def ksa(key: bytes):
    S = list(range(256))
    j = 0
    for i in range(257):
        idx = i & 0xFF
        j = (j + S[idx] + key[i % len(key)]) & 0xFF
        S[idx], S[j] = S[j], S[idx]
    return S


def prga(S, data: bytes) -> bytes:
    out = bytearray()
    i = j = 0
    for c in data:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) & 0xFF])
    return bytes(out)


flag = prga(ksa(KEY), CIPHER)
print(f"[+] flag = {flag.decode()}")

binary = sys.argv[1] if len(sys.argv) > 1 else "../attachment/new_RC4.exe"


def run(cmd):
    return subprocess.run(
        cmd, input=flag.decode() + "\n", capture_output=True, text=True, timeout=30
    ).stdout


try:
    try:
        out = run([binary])
    except OSError:
        out = run(["wine", binary])
    print("[+] verify:", "Correct" in out)
except FileNotFoundError:
    print("[!] binary not built yet, run: docker build -t rev-new-rc4 ../attachment")
