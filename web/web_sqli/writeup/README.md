# web_sqli Writeup 索引

- `wp.md`：完整解题思路（注入点定位、去空白限制下的 payload 构造、票据跳转链、修复建议）
- `exp.py`：利用链条 PoC（错误口令 -> `admin'--` 注入登录 -> 门户页 -> 提取 flag），纯标准库

```bash
python3 exp.py http://HOST:58000
```
