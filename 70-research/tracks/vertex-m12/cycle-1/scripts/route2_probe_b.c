/* 探针 B：CLI 参数解析 + fopen(argv 路径) + mpq_set_str */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <gmp.h>

static long long parse_ll(const char *s, const char *what, long long lo, long long hi)
{
    errno = 0;
    char *end = NULL;
    long long v = strtoll(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v < lo || v > hi) {
        fprintf(stderr, "参数 %s 非法：%s\n", what, s);
        exit(1);
    }
    return v;
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr, "用法：%s <Wstr> <M> <out_path>\n", argv[0]);
        return 1;
    }
    mpq_t w;
    mpq_init(w);
    if (mpq_set_str(w, argv[1], 10) != 0) {
        fprintf(stderr, "W 解析失败\n");
        return 1;
    }
    mpq_canonicalize(w);
    long long m = parse_ll(argv[2], "M", 2, 16);
    FILE *f = fopen(argv[3], "wb");
    if (!f)
        return 4;
    unsigned char c = (unsigned char)m;
    fwrite(&c, 1, 1, f);
    fclose(f);
    gmp_printf("%Qd\n", w);
    return 0;
}
