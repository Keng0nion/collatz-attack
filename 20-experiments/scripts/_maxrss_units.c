/* 量程测试：确认本机 getrusage 的 ru_maxrss 单位 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>

int main(void)
{
    struct rusage r0;
    getrusage(RUSAGE_SELF, &r0);
    printf("分配前 ru_maxrss = %ld\n", (long)r0.ru_maxrss);

    size_t n = 128 * 1024 * 1024;          /* 2 GiB 若元素 16 字节 */
    unsigned long long *p = malloc(n * 16);
    if (!p) { printf("分配失败\n"); return 1; }
    volatile unsigned long long *vp = p;
    for (size_t i = 0; i < n * 2; i++) vp[i] = i;   /* volatile：全量触碰，编译器不可省 */
    unsigned long long s = 0;
    for (size_t i = 0; i < n * 2; i++) s += p[i];
    printf("校验和 = %llu\n", s);
    struct rusage r1;
    getrusage(RUSAGE_SELF, &r1);
    printf("分配 2 GiB 并触碰后 ru_maxrss = %ld\n", (long)r1.ru_maxrss);
    printf("两者之差 = %ld\n", (long)(r1.ru_maxrss - r0.ru_maxrss));
    printf("对照组：实际申请字节数 = %.0f\n", (double)n * 16);
    return 0;
}
