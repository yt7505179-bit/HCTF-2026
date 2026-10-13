#!/usr/bin/env python3
"""出题人本地/容器验收：按对话表回答两轮寒暄 + XOR 0x5b。
选手 wp 不要靠这份脚本，应 IDA 找 chat1..chat8 / chatx。
用法: python exp.py [host] [port]
"""
import socket
import sys

XOR_KEY = 0x5B
ANSWERS = {
    "HELLO": "H0w d0 U d0",
    "HOW IS EVERYTHING GOING": "N0t t00 b4d",
    "NICE TO MEET YOU": "N1c3 t0 m33t U 2",
    "GOOD MORNING": "G00d m0rn1ng t0 U",
    "HAVE A NICE DAY": "U 2 h4v3 4 n1c3 d4y",
    "LONG TIME NO SEE": "Y34h 1t h4s b33n",
    "HOW DO YOU DO": "I d0 v3ry w3ll",
    "TAKE CARE": "U t4k3 c4r3 2",
}


def recvl(sock: socket.socket) -> str:
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("closed, got %r" % buf)
        buf += chunk
    return buf.decode().rstrip("\r\n")


def sendl(sock: socket.socket, s: str) -> None:
    sock.sendall((s + "\n").encode())


def solve(host: str, port: int) -> str:
    sock = socket.create_connection((host, port), timeout=10)
    try:
        for _ in range(2):
            q = recvl(sock)
            if q not in ANSWERS:
                raise RuntimeError("unknown question: %r" % q)
            sendl(sock, ANSWERS[q])
        tag = recvl(sock)
        if tag != "PLEASE XOR THIS":
            raise RuntimeError("expect XOR tag, got %r" % tag)
        hx = recvl(sock)
        raw = bytes.fromhex(hx)
        plain = bytes(b ^ XOR_KEY for b in raw).decode("ascii")
        sendl(sock, plain)
        flag = recvl(sock)
        if flag == "WRONG":
            raise RuntimeError("rejected")
        return flag
    finally:
        sock.close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
    print(solve(host, port))
