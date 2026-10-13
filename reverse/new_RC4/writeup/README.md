# new_RC4 writeup

## 思路

1. 附件 `new_RC4.exe` 是 PyInstaller `--onefile` 打包的 Windows PE。
   直接用 `strings` 只能看到引导外壳，看不到真正的逻辑。
2. 用 [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor) 解包：

   ```bash
   python3 pyinstxtractor.py new_RC4.exe
   # 得到 new_RC4.exe_extracted/ 目录，里面有 new_RC4.pyc
   ```

3. 反编译 `new_RC4.pyc`（如 `pycdc new_RC4.pyc`，或 `decompyle3` / `uncompyle6`），
   拿到加密逻辑：

   - 密钥 `KEY = b"so_love_this"`
   - 内置密文 `CIPHER`
   - `ksa()` 的循环是 `range(257)`，不是标准 RC4 的 256
   - `prga()` 是标准 RC4 的 keystream 异或

4. RC4 是对称流密码，加密和解密是同一个操作。因此直接对密文再跑一遍
   `prga(ksa(KEY), CIPHER)` 即可还原明文，得到 flag。

## exp

见 [`exp.py`](./exp.py)：

```bash
python3 exp.py
# [+] flag = HCTF{n3w_rc4_w1th_257_ksa}
```

如果本地构建了附件镜像，也可以用 wine 跑题目二进制验证：

```bash
docker build -t rev-new-rc4 ../attachment
docker run --rm -it rev-new-rc4
# flag: HCTF{n3w_rc4_w1th_257_ksa}
# Correct!
```

## flag

```
HCTF{n3w_rc4_w1th_257_ksa}
```
