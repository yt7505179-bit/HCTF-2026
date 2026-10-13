#ifndef PROTO_H
#define PROTO_H

/*
 * HCTF 2026 新生赛 · 文本对话
 * 行协议：一行一句，以 '\n' 结束。
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define LINE_MAX 128
#define XOR_KEY  0x5b
#define XOR_N    8

/* 静态附件互聊拿到的模板 / 假 flag，交平台不得分 */
#define TEMPLATE_FLAG "HCTF{1bab71b8-117f-4dea-a047-340b72101d7b}"

int write_all(int fd, const void *buf, int n);
int read_all(int fd, void *buf, int n);
int send_line(int fd, const char *s);
int recv_line(int fd, char *buf, int cap);
void xor_buf(unsigned char *p, int n, unsigned char key);
int bytes_to_hex(const unsigned char *in, int n, char *out, int cap);
int hex_to_bytes(const char *hex, unsigned char *out, int maxn);

#endif
