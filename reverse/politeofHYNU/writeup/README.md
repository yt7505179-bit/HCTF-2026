# 题解 · 衡师人真讲礼貌（politeofHYNU）

## 0. 诱饵

```text
$ strings client.elf | grep HCTF
HCTF{1bab71b8-117f-4dea-a047-340b72101d7b}
```

本地把 `server.elf` 和 `client.elf` 跑起来也会打出这一串。交平台是错的，这是模板。

`nc` 连远端会看到一行大写英文（例如 `HELLO`），不是二进制乱码。先别急着交 strings 里那串。

## 1. 先看它怎么开口

```text
$ nc host port
HELLO
```

或另一次：

```text
GOOD MORNING
```

每次前两句从若干寒暄里随机抽。第三句固定是：

```text
PLEASE XOR THIS
<16 个 hex 字符>
```

答错会回 `WRONG` 然后断开。不要写一个脚本把整场代打完就交，先把两个 ELF 在 IDA 里看清楚。

## 2. IDA 打开 client.elf

文件是 x86-64、未 strip、无 PIE。Functions 窗口能看到：

```text
chat1  chat2  chat3  chat4
chat5  chat6  chat7  chat8
chatx  chat   main
```

名字本身不说明内容，要点进函数看字符串。

`main` 里：`rand() % 8` 抽两个不同编号，各调一次 `chat(n)`，再调 `chatx()`，最后把 flag 打出去。

`chat` 是 switch，`case 0` 走 `chat1`，`case 1` 走 `chat2`，依此类推到 `chat8`。

每个 `chatN` 同一套路：

1. `send_line` 发出一句大写寒暄
2. `recv_line` 读你的一行
3. `strcmp` 和写死的 leetspeak 比，不对就 `WRONG`

把 8 个函数的 `strcmp` 第二参数抄下来，就是对话表。

`server.elf` 里同样有 `chat1`～`chat8`，方向反过来：收到那句寒暄就回对应 leetspeak。两份对上看，表就齐了。

## 3. 对话大全（寒暄两轮从这里抽）

| 函数 | 容器 / Client 先说 | 你必须一字不差地回 |
|------|-------------------|-------------------|
| chat1 | HELLO | H0w d0 U d0 |
| chat2 | HOW IS EVERYTHING GOING | N0t t00 b4d |
| chat3 | NICE TO MEET YOU | N1c3 t0 m33t U 2 |
| chat4 | GOOD MORNING | G00d m0rn1ng t0 U |
| chat5 | HAVE A NICE DAY | U 2 h4v3 4 n1c3 d4y |
| chat6 | LONG TIME NO SEE | Y34h 1t h4s b33n |
| chat7 | HOW DO YOU DO | I d0 v3ry w3ll |
| chat8 | TAKE CARE | U t4k3 c4r3 2 |

一次连接只问其中两句，顺序随机。表外的回答一律失败。

## 4. 第三轮：IDA 看 chatx

`chatx` 不在上面那张表里。它会：

1. 生成 8 字节字母数字
2. 每个字节 XOR `0x5b`（立即数，反编译里一眼能看到）
3. 先发一行 `PLEASE XOR THIS`
4. 再发一行 hex（16 个字符）
5. 等你把 **XOR 回去的 8 字节明文** 发回去

手算示例：

```text
PLEASE XOR THIS
1b0a191a0b4a1b0a
```

每个字节 `^ 0x5b`：

```text
python3 -c "print(bytes(b^0x5b for b in bytes.fromhex('1b0a191a0b4a1b0a')).decode())"
```

把得到的 8 个可打印字符原样打回去（不要再包一层 hex）。

`server.elf` 的 `chatx` 是同一把钥匙 `0x5b`，本地互聊时它替你算。

## 5. 和终端交互

连上后按 IDA 抄下来的表回，不要手敲二进制。

```text
$ nc host port
HELLO
H0w d0 U d0
TAKE CARE
U t4k3 c4r3 2
PLEASE XOR THIS
<16 hex>
<这里贴 XOR 0x5b 之后的 8 个字符>
HCTF{........-....-....-....-............}
```

前两句每次可能换。第三句算完 XOR 就会给 flag。

本地附件互聊打出的仍是模板 `HCTF{1bab71b8-117f-4dea-a047-340b72101d7b}`，只有远端 GRANT 那行才是真的。
