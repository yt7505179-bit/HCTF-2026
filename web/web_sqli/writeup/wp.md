# web_sqli Writeup

## 漏洞点

登录接口 `POST /lyuapServer/v1/tickets` 把账号口令直接字符串拼进 SQL：

```sql
SELECT * FROM users WHERE account = '{username}' AND password = '{password}' LIMIT 1
```

命中任意一行即以该行身份发放登录票据（TGT/ST），前端自动跳转门户
`/sc/portal`。库中首个用户是系统管理员（`account = admin`），其
「网络安全宣传周内部公告」字段即真 flag（部署时由 `FLAG` 环境变量注入）。

## 利用思路

1. 打开登录页，右下角「点击查看登录方法」->
   `https://baidu.ma/?q=Q1RG6aKY55uuLOWmguS9lVNRTOazqOWFpee7lei/h+eZu+W9lQ==`，
   query 是 Base64，解码为「CTF题目,如何SQL注入绕过登录」——一道百度搜索，
   就是本题的官方教程入口。
2. 注意前端会把输入中的所有空白字符剥掉（`replace(/\s+/g,"")`），所以
   页面上的 payload 不能带空格；`--` 是 SQL 行注释，后面整段口令比较被吃掉：

   | 用户名 | 密码 | 效果 |
   |---|---|---|
   | `admin'--` | 随意 | `account='admin'` 命中管理员，口令比较被注释 |
   | `'or'1'='1'--` | 随意 | 恒真条件返回首行（即管理员） |

3. 登录成功后前端携带 `service=/sc/portal`（`loginType.json` 的
   `defaultLoginUrl`）自动跳转 `/sc/portal?ticket=ST-...`，门户校验票据
   渲染「登录成功 · 当前身份」，管理员身份即可看到内部公告里的
   `hctf{...}`。
4. 直接打 HTTP 接口（不经页面）则不受去空白限制，经典全空格姿势如
   `admin' -- `、`' OR '1'='1' -- ` 同样成立；口令字段在页面登录时会被
   前端 RSA 加密传输，因此页面上只注入用户名一侧。

## exp

```bash
python3 exp.py http://HOST:58000
```

`exp.py` 无第三方依赖：错误口令演示失败 -> `admin'--` 登录拿票据 ->
请求门户页 -> 正则提取 flag。

## 修复建议

参数化查询（占位符），永远不要把用户输入拼进 SQL 语句：

```python
conn.execute("SELECT * FROM users WHERE account = ? AND password = ?", (u, p))
```
