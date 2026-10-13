#include "proto.h"

int write_all(int fd, const void *buf, int n)
{
    const unsigned char *p = (const unsigned char *)buf;
    int off = 0;
    while (off < n) {
        int w = (int)write(fd, p + off, (size_t)(n - off));
        if (w <= 0)
            return -1;
        off += w;
    }
    return 0;
}

int read_all(int fd, void *buf, int n)
{
    unsigned char *p = (unsigned char *)buf;
    int off = 0;
    while (off < n) {
        int r = (int)read(fd, p + off, (size_t)(n - off));
        if (r <= 0)
            return -1;
        off += r;
    }
    return 0;
}

int send_line(int fd, const char *s)
{
    int n = (int)strlen(s);
    if (write_all(fd, s, n) < 0)
        return -1;
    return write_all(fd, "\n", 1);
}

int recv_line(int fd, char *buf, int cap)
{
    int n = 0;
    if (cap < 2)
        return -1;
    while (n < cap - 1) {
        unsigned char c;
        if (read_all(fd, &c, 1) < 0)
            return -1;
        if (c == '\n')
            break;
        if (c == '\r')
            continue;
        buf[n++] = (char)c;
    }
    buf[n] = '\0';
    return n;
}

void xor_buf(unsigned char *p, int n, unsigned char key)
{
    int i;
    for (i = 0; i < n; i++)
        p[i] = (unsigned char)(p[i] ^ key);
}

int bytes_to_hex(const unsigned char *in, int n, char *out, int cap)
{
    static const char *d = "0123456789abcdef";
    int i;
    if (cap < n * 2 + 1)
        return -1;
    for (i = 0; i < n; i++) {
        out[i * 2] = d[(in[i] >> 4) & 0xf];
        out[i * 2 + 1] = d[in[i] & 0xf];
    }
    out[n * 2] = '\0';
    return n * 2;
}

static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9')
        return c - '0';
    if (c >= 'a' && c <= 'f')
        return c - 'a' + 10;
    if (c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    return -1;
}

int hex_to_bytes(const char *hex, unsigned char *out, int maxn)
{
    int i, n;
    n = (int)strlen(hex);
    if (n == 0 || (n & 1) != 0 || n / 2 > maxn)
        return -1;
    for (i = 0; i < n / 2; i++) {
        int hi = hex_nibble(hex[i * 2]);
        int lo = hex_nibble(hex[i * 2 + 1]);
        if (hi < 0 || lo < 0)
            return -1;
        out[i] = (unsigned char)((hi << 4) | lo);
    }
    return n / 2;
}
