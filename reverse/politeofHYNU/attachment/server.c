/*
 * HCTF 2026 新生赛 · Reverse · Server
 *
 *   ./server.elf [port]     默认 2333
 *
 * 只用于附件本地互聊。答对之后若收到的是模板 flag 就打印；
 * 其它内容拒绝打印，避免把本程序 socat 到远端直接出真 flag。
 */
#include "proto.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/socket.h>

static void send_err(int fd)
{
    send_line(fd, "WRONG");
}

int chat1(int fd, const char *q)
{
    if (strcmp(q, "HELLO") != 0)
        return 0;
    if (send_line(fd, "H0w d0 U d0") < 0)
        return -1;
    return 1;
}

int chat2(int fd, const char *q)
{
    if (strcmp(q, "HOW IS EVERYTHING GOING") != 0)
        return 0;
    if (send_line(fd, "N0t t00 b4d") < 0)
        return -1;
    return 1;
}

int chat3(int fd, const char *q)
{
    if (strcmp(q, "NICE TO MEET YOU") != 0)
        return 0;
    if (send_line(fd, "N1c3 t0 m33t U 2") < 0)
        return -1;
    return 1;
}

int chat4(int fd, const char *q)
{
    if (strcmp(q, "GOOD MORNING") != 0)
        return 0;
    if (send_line(fd, "G00d m0rn1ng t0 U") < 0)
        return -1;
    return 1;
}

int chat5(int fd, const char *q)
{
    if (strcmp(q, "HAVE A NICE DAY") != 0)
        return 0;
    if (send_line(fd, "U 2 h4v3 4 n1c3 d4y") < 0)
        return -1;
    return 1;
}

int chat6(int fd, const char *q)
{
    if (strcmp(q, "LONG TIME NO SEE") != 0)
        return 0;
    if (send_line(fd, "Y34h 1t h4s b33n") < 0)
        return -1;
    return 1;
}

int chat7(int fd, const char *q)
{
    if (strcmp(q, "HOW DO YOU DO") != 0)
        return 0;
    if (send_line(fd, "I d0 v3ry w3ll") < 0)
        return -1;
    return 1;
}

int chat8(int fd, const char *q)
{
    if (strcmp(q, "TAKE CARE") != 0)
        return 0;
    if (send_line(fd, "U t4k3 c4r3 2") < 0)
        return -1;
    return 1;
}

int chatx(int fd)
{
    char tag[LINE_MAX];
    char hex[LINE_MAX];
    unsigned char raw[XOR_N];
    char plain[XOR_N + 1];
    int n;

    if (recv_line(fd, tag, sizeof(tag)) < 0)
        return -1;
    if (strcmp(tag, "PLEASE XOR THIS") != 0)
        return -1;
    if (recv_line(fd, hex, sizeof(hex)) < 0)
        return -1;
    n = hex_to_bytes(hex, raw, XOR_N);
    if (n != XOR_N)
        return -1;
    xor_buf(raw, XOR_N, XOR_KEY);
    memcpy(plain, raw, XOR_N);
    plain[XOR_N] = '\0';
    return send_line(fd, plain);
}

static int handle_talk(int fd)
{
    char q[LINE_MAX];
    int r;

    if (recv_line(fd, q, sizeof(q)) < 0)
        return -1;
    r = chat1(fd, q);
    if (r != 0)
        return r;
    r = chat2(fd, q);
    if (r != 0)
        return r;
    r = chat3(fd, q);
    if (r != 0)
        return r;
    r = chat4(fd, q);
    if (r != 0)
        return r;
    r = chat5(fd, q);
    if (r != 0)
        return r;
    r = chat6(fd, q);
    if (r != 0)
        return r;
    r = chat7(fd, q);
    if (r != 0)
        return r;
    r = chat8(fd, q);
    if (r != 0)
        return r;
    return -1;
}

static int handle_client(int fd)
{
    char grant[LINE_MAX];

    if (handle_talk(fd) != 1) {
        send_err(fd);
        return -1;
    }
    if (handle_talk(fd) != 1) {
        send_err(fd);
        return -1;
    }
    if (chatx(fd) < 0) {
        send_err(fd);
        return -1;
    }
    if (recv_line(fd, grant, sizeof(grant)) < 0) {
        send_err(fd);
        return -1;
    }
    if (strcmp(grant, TEMPLATE_FLAG) != 0) {
        send_err(fd);
        fprintf(stderr, "[server] refuse non-template grant\n");
        return -1;
    }
    printf("%s\n", grant);
    fflush(stdout);
    return 0;
}

int main(int argc, char **argv)
{
    int srv, opt = 1;
    int port = 2333;
    struct sockaddr_in addr;

    if (argc >= 2)
        port = atoi(argv[1]);

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    signal(SIGCHLD, SIG_IGN);
    signal(SIGPIPE, SIG_IGN);

    srv = socket(AF_INET, SOCK_STREAM, 0);
    if (srv < 0)
        return 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((unsigned short)port);
    if (bind(srv, (struct sockaddr *)&addr, sizeof(addr)) < 0)
        return 1;
    if (listen(srv, 16) < 0)
        return 1;

    fprintf(stderr, "[server] listen 0.0.0.0:%d\n", port);

    for (;;) {
        int cli = accept(srv, NULL, NULL);
        pid_t pid;
        if (cli < 0)
            continue;
        pid = fork();
        if (pid == 0) {
            close(srv);
            alarm(30);
            handle_client(cli);
            close(cli);
            _exit(0);
        }
        close(cli);
        (void)pid;
    }
}
