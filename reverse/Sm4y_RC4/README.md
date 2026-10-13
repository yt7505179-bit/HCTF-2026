# Sm4y_RC4

出题人：0

- 方向：Reverse
- 难度：中等 / Medium
- 考点：PyInstaller 打包逆向、pyc 反编译、自定义 RC4（KSA 257 轮）

## 题目描述

附件是一个用 PyInstaller 打包出来的命令行程序，输入 flag 后程序会对其进行
“加密”并与内置密文比对，正确才会输出 `Correct!`。

加密算法看起来像 RC4，但出题人偷偷改了密钥调度：标准的 KSA 只跑 256 轮，
这里跑的是 257 轮。把程序脱壳、反编译出源码，还原出被改动的 RC4，再把整个过程
反过来跑一遍即可拿到 flag。

## 题目信息

- 附件：`attachment/Sm4y_RC4.exe`（选手下载，Windows PE，PyInstaller 单文件打包）
- 远程连接：无（离线题目）
- Flag 格式：`HCTF{...}`
- 运行环境：Windows；Linux / macOS 下可用 `wine` 运行

## 提示

- 这是 PyInstaller 单文件（`--onefile`）打包的 exe，直接 `strings` 只能看到外壳
- 先用 `pyinstxtractor` 解包，得到内部的 `Sm4y_RC4.pyc`
- `pyc` 可以用 `pycdc` / `decompyle3` 之类的工具反编译回近似源码
- 加密核心是 RC4，但 KSA 的循环次数不是 256
- RC4 加解密对称：把内置密文当作输入再跑一遍同样的 `prga(ksa(KEY), data)` 即可还原

## 本地构建与运行

`attachment/` 下的 Dockerfile 通过 Wine + PyInstaller 交叉打包出 Windows PE
（`builder` 阶段，CI 从 `/build` 提取 `.exe` 并作为附件发布）：

```bash
# 构建
docker build -t rev-sm4y-rc4 ./attachment

# 运行（wine 执行题目 exe）
docker run --rm -it rev-sm4y-rc4
```

也可以在有 Windows Python 的机器上直接打包：

```bash
cd attachment
pip install pyinstaller
pyinstaller --onefile --name Sm4y_RC4 Sm4y_RC4.py
dist/Sm4y_RC4.exe
```

## 目录结构

```
Sm4y_RC4/
├── README.md            # 题目说明（本文件）
├── attachment/          # 【公开】给选手的附件与构建 Dockerfile
│   ├── Sm4y_RC4.py      # 题目源码（PyInstaller 打包输入）
│   └── Dockerfile
├── src/                 # 【私密】出题脚本
│   └── gen.py           # 由 flag 生成内置密文
└── writeup/             # 【私密】解题思路与 exp
    ├── exp.py
    └── README.md
```

## 部署说明

本题为离线逆向题，无需远程服务，也不需要在 `src/` 下写 Dockerfile。
`attachment/Dockerfile` 采用多阶段构建：`builder` 阶段使用
`batonogov/pyinstaller-windows`（Ubuntu + Wine + Windows Python + PyInstaller）
在 Linux/amd64 下打包出 Windows PE，CI 会从 `/build` 中提取并作为附件发布；
运行阶段使用 `debian:bookworm-slim` + `wine` 方便本地验证。
