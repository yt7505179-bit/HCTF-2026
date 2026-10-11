# -*- coding: utf-8 -*-
"""统一身份认证平台 · CTF 复刻后端（web_sqli：SQL 注入登录绕过）

与 web_pathconfusion / web_leakedkey / web_headerauth 同一系列的门户切片，
独立部署、独立可解：

  - 登录口 POST /lyuapServer/v1/tickets 把账号口令直接拼进 SQL（本题考点），
    注入成功即以命中行对应的身份登录（首个用户为系统管理员 admin）
  - 登录成功后按前端约定的响应形状发放 TGT/ST 票据，前端携带
    service（取 loginType.json 的 defaultLoginUrl = /sc/portal）跳转门户
  - /sc/portal 门户首页：校验 ?ticket= 或 CASTGC Cookie，管理员身份可见
    「网络安全宣传周内部公告」——真 flag（seed 时由 FLAG 环境变量注入）
  - 其余查询一律参数化；非账户登录通道（短信/扫码等）与上题一样不可用

前端会把输入中的空白字符全部剥掉，因此页面上的注入 payload 不含空格
（admin'-- / 'or'1'='1'--）；直接打 HTTP 接口则不受此限制。
"""
import json
import sqlite3
import time
import uuid
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)

BASE = Path(__file__).parent
DB_PATH = BASE / "data" / "cas.db"

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# ----------------------------------------------------------------------
# 登录页配置（与系列题同源，仅 defaultLoginUrl 指向本题门户页）
# ----------------------------------------------------------------------
LOGIN_TYPE = json.loads(
    (BASE / "config" / "loginType.json").read_text(encoding="utf-8")
)

# 会话票据：TGT（CASTGC Cookie，长效）与 ST（?ticket=，短效）→ (userId, 过期)
TGC_TTL = LOGIN_TYPE["data"].get("tgcTimeout", 3600)
ST_TTL = 300
SESSIONS: dict = {}


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def new_ticket(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def issue(uid: str, ttl: int, prefix: str) -> str:
    t = new_ticket(prefix)
    SESSIONS[t] = (uid, time.time() + ttl)
    return t


def resolve_user(request: Request):
    """按 ?ticket= 或 CASTGC Cookie 找当前登录用户，失败返回 None。"""
    for key in (request.query_params.get("ticket", ""), request.cookies.get("CASTGC", "")):
        hit = SESSIONS.get(key)
        if hit and hit[1] >= time.time():
            conn = db()
            try:
                row = conn.execute(
                    "SELECT * FROM users WHERE userId = ?", (hit[0],)
                ).fetchone()
            finally:
                conn.close()
            return row
    return None


# ----------------------------------------------------------------------
# 登录页配置接口（gohome.js 的 receiveLoginData 带尾斜杠请求，两种都注册）
# ----------------------------------------------------------------------
@app.get("/lyuapServer/loginType")
@app.get("/lyuapServer/loginType/")
async def login_type():
    return JSONResponse(LOGIN_TYPE)


@app.get("/lyuapServer/UKey/getRandom")
async def ukey_random():
    return JSONResponse({"data": {"random": uuid.uuid4().hex}})


# ----------------------------------------------------------------------
# 登录：账号口令直接拼进 SQL（复刻未整改的老代码）
# ----------------------------------------------------------------------
@app.post("/lyuapServer/v1/tickets")
async def tickets(request: Request):
    # 前端以 x-www-form-urlencoded 提交（qs.stringify），手工解析以免
    # 不同 FastAPI/Starlette 版本对 form 解析的 multipart 依赖差异
    form = parse_qs((await request.body()).decode("utf-8", "replace"))
    username = form.get("username", [""])[0]
    password = form.get("password", [""])[0]

    # 漏洞点：字符串拼接。前端对 password 另有 RSA 加密传输，
    # 服务端拿到什么比什么——但注入只需让 WHERE 提前闭合即可绕过口令比较。
    sql = (
        "SELECT * FROM users WHERE account = '%s' AND password = '%s' LIMIT 1"
        % (username, password)
    )
    conn = db()
    try:
        row = conn.execute(sql).fetchone()
    except sqlite3.OperationalError:
        # 注入写坏语法时与口令错误同形返回，不泄露报错细节
        row = None
    finally:
        conn.close()

    if row is None:
        # 前端渲染「用户名或密码错误。」
        return JSONResponse({"data": {"code": "NOUSER", "uid": "", "vcodes": ""}})

    tgt = issue(row["userId"], TGC_TTL, "TGT")
    st = issue(row["userId"], ST_TTL, "ST")
    # 前端约定的成功形状：顶层 tgt/ticket（无 data.code）
    return JSONResponse({"tgt": tgt, "ticket": st})


@app.post("/lyuapServer/v1/tickets/{tgt}")
async def ticket_grant(request: Request, tgt: str):
    """携 service 换新 ST（gohome.js 已登录时的自动续跳）。"""
    hit = SESSIONS.get(tgt)
    if not hit or hit[1] < time.time():
        return PlainTextResponse("INVALID")
    return PlainTextResponse(issue(hit[0], ST_TTL, "ST"))


# ----------------------------------------------------------------------
# 门户首页（defaultLoginUrl 落点）
# ----------------------------------------------------------------------
PORTAL_CSS = """
  body{font-family:"Microsoft YaHei",Arial,sans-serif;background:#eef2f7;margin:0;min-height:100vh;display:flex;flex-direction:column;}
  .top{background:#3980f0;color:#fff;height:56px;display:flex;align-items:center;padding:0 32px;font-size:18px;letter-spacing:1px;}
  .top small{margin-left:12px;font-size:12px;opacity:.85;}
  .top .out{margin-left:auto;font-size:13px;color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.6);border-radius:3px;padding:4px 12px;}
  .wrap{width:min(860px,92vw);margin:36px auto;flex:1;}
  .card{background:#fff;border-radius:6px;box-shadow:0 1px 4px rgba(31,60,100,.12);padding:26px 30px;margin-bottom:22px;}
  .card h2{font-size:17px;color:#1f6fb2;margin:0 0 14px;padding-bottom:10px;border-bottom:2px solid #e8eef6;}
  .kv{display:flex;flex-wrap:wrap;}
  .kv div{width:33%;font-size:14px;color:#444;line-height:2.1;}
  .kv b{color:#333;font-weight:600;margin-right:6px;}
  .notice li{font-size:14px;color:#444;line-height:2;}
  .notice ul{padding-left:20px;margin:0;}
  .flagline{margin-top:14px;background:#f2f8ff;border:1px dashed #7db2f5;border-radius:6px;padding:14px 18px;font-size:15px;}
  .flagline code{font-family:Consolas,monospace;font-size:16px;color:#0b5bb5;background:#e4effc;padding:2px 8px;border-radius:4px;}
  .foot{text-align:center;color:#8aa0b8;font-size:12px;padding:18px 0 26px;line-height:1.9;}
  .deny{background:#fff7e6;border:1px solid #ffd591;border-radius:6px;padding:12px 16px;font-size:13px;color:#7a5b12;margin-top:14px;}
"""

PORTAL_FOOT = (
    "<div class=\"foot\">Copyright @2018 CTF ORG. All Rights Reserved."
    " 本页面为 CTF 比赛复刻环境，与任何真实学校无关</div>"
)


def esc(v) -> str:
    return (
        str(v)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def portal_html(user: sqlite3.Row) -> str:
    is_admin = str(user["userId"]) == "1"
    info = "".join(
        f'<div><b>{k}</b>{esc(user[f])}</div>'
        for k, f in [
            ("姓名：", "userName"),
            ("账号：", "account"),
            ("身份：", "orgName"),
            ("部门：", "professional"),
            ("状态：", "status"),
            ("最近登录：", "lastLogin"),
        ]
    )
    if is_admin:
        flag_box = (
            '<div class="flagline">网络安全宣传周 · 管理员内部公告（仅管理员身份可见）：<br>'
            f'<code>{esc(user["description"])}</code></div>'
        )
    else:
        flag_box = (
            '<div class="deny">管理员内部公告仅对管理员身份开放——'
            "当前是普通用户会话，试试以管理员身份登录。</div>"
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>统一身份认证平台 · 门户</title>
<style>{PORTAL_CSS}</style>
</head>
<body>
<div class="top">统一身份认证平台<small>门户 Portal</small>
  <a class="out" href="/sc/portal/logout">退出登录</a></div>
<div class="wrap">
  <div class="card">
    <h2>登录成功 · 当前身份</h2>
    <div class="kv">{info}</div>
  </div>
  <div class="card notice">
    <h2>通知公告</h2>
    <ul>
      <li>关于 2026 年秋季学期统一身份认证平台切换维护的通知（2026-09-10）</li>
      <li>提醒：请勿在公共电脑上勾选「七天之内记住密码」（2026-09-02）</li>
    </ul>
    {flag_box}
  </div>
</div>
{PORTAL_FOOT}
</body>
</html>"""


@app.get("/sc/portal", response_class=HTMLResponse)
async def portal(request: Request):
    user = resolve_user(request)
    if user is None:
        return RedirectResponse(url="/", status_code=302)
    return HTMLResponse(portal_html(user))


@app.get("/sc/portal/logout")
async def logout(request: Request):
    for key in (request.cookies.get("CASTGC", ""), request.query_params.get("ticket", "")):
        SESSIONS.pop(key, None)
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("CASTGC", path="/")
    return resp


# ----------------------------------------------------------------------
# 兜底：记录前端 SPA 打到后端的未知路径（联调观察用）
# ----------------------------------------------------------------------
@app.api_route("/{rest:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def fallback(request: Request, rest: str):
    return JSONResponse({"code": 404, "msg": f"not found: {rest}"}, status_code=404)
