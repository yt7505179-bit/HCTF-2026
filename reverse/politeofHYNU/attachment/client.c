/*
 * HCTF 2026 新生赛 · Reverse · Client
 *
 *   ./client.elf <host> <port>   本地 TCP，连附件里的 server.elf
 *   ./client.elf                 无参走 stdin/stdout（容器 wrap 用）
 *
 * 对端答对两轮随机寒暄 + 一轮 XOR 之后，Client 把 flag 发给它。
 * FLAG 环境变量或 /flag 优先；都没有则发模板假 flag。
 */
#include "proto.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/socket.h>
#include <time.h>

static int g_in = STDIN_FILENO;
static int g_out = STDOUT_FILENO;

static void die(void)
{
    send_line(g_out, "WRONG");
    _exit(1);
}

static void expect(const char *want)
{
    char buf[LINE_MAX];
    if (recv_line(g_in, buf, sizeof(buf)) < 0)
        die();
    if (strcmp(buf, want) != 0)
        die();
}

static void load_flag(char *buf, size_t n)
{
    const char *env = getenv("FLAG");
    FILE *fp;

    if (env != NULL && env[0] != '\0') {
        snprintf(buf, n, "%s", env);
        return;
    }
    fp = fopen("/flag", "r");
    if (fp != NULL) {
        if (fgets(buf, (int)n, fp) != NULL) {
            buf[strcspn(buf, "\r\n")] = '\0';
            fclose(fp);
            if (buf[0] != '\0')
                return;
        } else {
            fclose(fp);
        }
    }
    snprintf(buf, n, "%s", TEMPLATE_FLAG);
}

void chat1(void)
{
    if (send_line(g_out, "HELLO") < 0)
        die();
    expect("H0w d0 U d0");
}

void chat2(void)
{
    if (send_line(g_out, "HOW IS EVERYTHING GOING") < 0)
        die();
    expect("N0t t00 b4d");
}

void chat3(void)
{
    if (send_line(g_out, "NICE TO MEET YOU") < 0)
        die();
    expect("N1c3 t0 m33t U 2");
}

void chat4(void)
{
    if (send_line(g_out, "GOOD MORNING") < 0)
        die();
    expect("G00d m0rn1ng t0 U");
}

void chat5(void)
{
    if (send_line(g_out, "HAVE A NICE DAY") < 0)
        die();
    expect("U 2 h4v3 4 n1c3 d4y");
}

void chat6(void)
{
    if (send_line(g_out, "LONG TIME NO SEE") < 0)
        die();
    expect("Y34h 1t h4s b33n");
}

void chat7(void)
{
    if (send_line(g_out, "HOW DO YOU DO") < 0)
        die();
    expect("I d0 v3ry w3ll");
}

void chat8(void)
{
    if (send_line(g_out, "TAKE CARE") < 0)
        die();
    expect("U t4k3 c4r3 2");
}

void chatx(void)
{
    static const char *tab =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    unsigned char plain[XOR_N];
    unsigned char wire[XOR_N];
    char hex[XOR_N * 2 + 1];
    char buf[LINE_MAX];
    int i;

    for (i = 0; i < XOR_N; i++)
        plain[i] = (unsigned char)tab[rand() % 62];
    memcpy(wire, plain, XOR_N);
    xor_buf(wire, XOR_N, XOR_KEY);
    if (bytes_to_hex(wire, XOR_N, hex, sizeof(hex)) < 0)
        die();
    if (send_line(g_out, "PLEASE XOR THIS") < 0)
        die();
    if (send_line(g_out, hex) < 0)
        die();
    if (recv_line(g_in, buf, sizeof(buf)) < 0)
        die();
    if ((int)strlen(buf) != XOR_N)
        die();
    if (memcmp(buf, plain, XOR_N) != 0)
        die();
}

static void send_grant(void)
{
    char flag[LINE_MAX];
    load_flag(flag, sizeof(flag));
    if (send_line(g_out, flag) < 0)
        die();
}

static void chat(int n)
{
    switch (n) {
    case 0:
        chat1();
        break;
    case 1:
        chat2();
        break;
    case 2:
        chat3();
        break;
    case 3:
        chat4();
        break;
    case 4:
        chat5();
        break;
    case 5:
        chat6();
        break;
    case 6:
        chat7();
        break;
    default:
        chat8();
        break;
    }
}

static int tcp_connect(const char *host, int port)
{
    int fd;
    struct sockaddr_in addr;

    fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0)
        return -1;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((unsigned short)port);
    if (inet_pton(AF_INET, host, &addr.sin_addr) != 1) {
        close(fd);
        return -1;
    }
    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

int main(int argc, char **argv)
{
    int sock = -1;
    int a, b;

    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    signal(SIGPIPE, SIG_IGN);
    signal(SIGALRM, SIG_DFL);
    alarm(60);
    srand((unsigned int)time(NULL) ^ (unsigned int)getpid());

    if (argc >= 3) {
        sock = tcp_connect(argv[1], atoi(argv[2]));
        if (sock < 0)
            return 1;
        g_in = sock;
        g_out = sock;
    } else if (argc == 2) {
        sock = tcp_connect("127.0.0.1", atoi(argv[1]));
        if (sock < 0)
            return 1;
        g_in = sock;
        g_out = sock;
    } else {
        g_in = STDIN_FILENO;
        g_out = STDOUT_FILENO;
    }

    a = rand() % 8;
    b = rand() % 8;
    while (b == a)
        b = rand() % 8;
    chat(a);
    chat(b);
    chatx();
    send_grant();

    if (sock >= 0)
        close(sock);
    return 0;
}
