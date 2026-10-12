#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sm4y_RC4 - HCTF 2026 Reverse.

Reads the flag from stdin and compares the encrypted result with the
embedded ciphertext.
"""


KEY    = b"so_love_this"
CIPHER = bytes.fromhex("64adfa8d80eaaef88b17a16af6347ade2c90e207138fcbc43fc8cb")


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


def main():
    inp = input("flag: ").encode()
    if prga(ksa(KEY), inp) == CIPHER:
        print("Correct!")
    else:
        print("Wrong.")


if __name__ == "__main__":
    main()
