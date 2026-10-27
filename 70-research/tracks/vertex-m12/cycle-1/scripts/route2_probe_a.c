/* 探针 A：GMP 字符串分配 + 倍增 realloc 拼接 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

static char *frac_str(const mpq_t q)
{
    char *np = mpz_get_str(NULL, 10, mpq_numref(q));
    char *dp = mpz_get_str(NULL, 10, mpq_denref(q));
    if (!np || !dp)
        return NULL;
    size_t ln = strlen(np), ld = strlen(dp);
    char *s = (char *)malloc(ln + ld + 2);
    if (!s) {
        free(np);
        free(dp);
        return NULL;
    }
    memcpy(s, np, ln);
    s[ln] = '/';
    memcpy(s + ln + 1, dp, ld);
    s[ln + ld + 1] = '\0';
    free(np);
    free(dp);
    return s;
}

static char *grow_join(const char **parts, int n)
{
    size_t cap = 64;
    char *buf = (char *)malloc(cap);
    if (!buf)
        return NULL;
    size_t len = 0;
    buf[0] = '\0';
    for (int i = 0; i < n; i++) {
        size_t lf = strlen(parts[i]);
        if (len + lf + 2 > cap) {
            size_t ncap = cap;
            while (len + lf + 2 > ncap)
                ncap *= 2;
            char *nb = (char *)realloc(buf, ncap);
            if (!nb) {
                free(buf);
                return NULL;
            }
            buf = nb;
            cap = ncap;
        }
        if (i)
            buf[len++] = ';';
        memcpy(buf + len, parts[i], lf);
        len += lf;
        buf[len] = '\0';
    }
    return buf;
}

int main(void)
{
    mpq_t q;
    mpq_init(q);
    mpq_set_ui(q, 126797, 80000);
    char *s = frac_str(q);
    printf("%s\n", s ? s : "(null)");
    free(s);
    mpq_clear(q);
    return 0;
}
