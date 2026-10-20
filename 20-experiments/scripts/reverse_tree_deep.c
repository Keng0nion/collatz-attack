/* reverse_tree_deep.c
 * 逆向树深度生长：从 1 出发，分支 x -> 2x 与 x -> (2x-1)/3（当且仅当 3 | 2x-1 且结果为正奇数）。
 * 与 Python 版互相独立实现，用于：
 *   1. 把 BFS 推到更深的层（Python 版受内存限制只能到 48 层左右）；
 *   2. 交叉校验：同深度下两版的逐层节点数必须逐层相等。
 *
 * 关键结构事实（Python 版已在 48 层内实测：全书只有一次「重复孩子」事件，即 2 -> 1）：
 * 每个非根节点的父节点唯一，故 BFS 各层互不相交，不需要全局哈希表，
 * 只需保存当前层与下一层两个数组。本程序仍对每一层做两项独立校验：
 *   (a) 层内严格递增（层内无重复）；
 *   (b) 每个孩子的「父节点」（按前向公式从孩子反算）确实在前一层里（二分查找）。
 *   两项合起来（归纳）即证明各层恰好是精确的 BFS 层且互不相交。
 *
 * 编译：cc -O3 -o reverse_tree_deep reverse_tree_deep.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>

typedef unsigned __int128 u128;

static int cmp_u128(const void *a, const void *b)
{
    u128 x = *(const u128 *)a, y = *(const u128 *)b;
    return (x < y) ? -1 : ((x > y) ? 1 : 0);
}

static void u128_to_str(u128 v, char *out)
{
    char tmp[64];
    int i = 0;
    if (v == 0) { out[0] = '0'; out[1] = 0; return; }
    while (v > 0) { tmp[i++] = (char)('0' + (int)(v % 10)); v /= 10; }
    for (int j = 0; j < i; j++) out[j] = tmp[i - 1 - j];
    out[i] = 0;
}

/* 二分查找：v 是否在已排序的 arr 中 */
static int contains(const u128 *arr, size_t n, u128 v)
{
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (arr[mid] < v) lo = mid + 1; else hi = mid;
    }
    return (lo < n && arr[lo] == v);
}

/* 父节点公式：偶 -> n/2；奇 -> (3n+1)/2 */
static u128 parent_of(u128 n)
{
    if ((n & 1) == 0) return n >> 1;
    return (3 * n + 1) >> 1;
}

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv)
{
    int max_depth = 60;
    int odd_list_depth = 20;
    int verify = 1;
    double mem_guard_gb = 5.0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--depth") && i + 1 < argc) max_depth = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--odd-list-depth") && i + 1 < argc) odd_list_depth = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--no-verify")) verify = 0;
        else if (!strcmp(argv[i], "--mem-guard-gb") && i + 1 < argc) mem_guard_gb = atof(argv[++i]);
    }

    printf("======================================================================\n");
    printf("逆向树深度生长（C 版，独立实现）\n");
    printf("分支：x -> 2x；x -> (2x-1)/3（当且仅当 3 | 2x-1 且结果为正奇数）\n");
    printf("最大深度 = %d；校验 = %s；内存保护 = %.1f GB\n",
           max_depth, verify ? "开" : "关", mem_guard_gb);
    printf("======================================================================\n");

    size_t cap_cur = 16, cap_nxt = 16;
    u128 *cur = malloc(cap_cur * sizeof(u128));
    u128 *nxt = malloc(cap_nxt * sizeof(u128));
    if (!cur || !nxt) { fprintf(stderr, "初始分配失败\n"); return 1; }
    cur[0] = 1;
    size_t ncur = 1, nnext = 0;

    int reached = 0;
    long long total_nodes = 0;
    unsigned long long collisions_skipped = 0;   /* 生成到 1 而被跳过的次数 */
    int verify_fail = 0;
    double t0 = now_s();
    char *buf = malloc(128);
    char *omn_s = malloc(128);
    char *omx_s = malloc(128);
    char *mx_s = malloc(128);
    size_t prev_size = 0;

    printf("%4s %14s %13s %13s %14s %8s %8s %10s %10s %10s %24s %24s\n",
           "d", "N(d)", "N(d)/N(d-1)", "(4/3)^d", "N/(4/3)^d",
           "odd", "even", "r=0", "r=1", "r=2", "min_odd", "max_odd");

    for (int d = 0; d <= max_depth; d++) {
        size_t n_odd = 0, r0 = 0, r1 = 0, r2 = 0, two_child = 0;
        u128 mn = cur[0], mx = cur[0], omn = 0, omx = 0;
        int have_odd = 0;
        for (size_t i = 0; i < ncur; i++) {
            u128 v = cur[i];
            if (v < mn) mn = v;
            if (v > mx) mx = v;
            if (v & 1) {
                n_odd++;
                if (!have_odd || v < omn) omn = v;
                if (!have_odd || v > omx) omx = v;
                have_odd = 1;
            }
            unsigned r = (unsigned)(v % 3);
            if (r == 0) r0++; else if (r == 1) r1++; else r2++;
            if (r == 2) two_child++;
        }
        (void)two_child;
        double pred = 1.0;
        for (int k = 0; k < d; k++) pred *= 4.0 / 3.0;
        u128_to_str(mn, buf);
        u128_to_str(mx, mx_s);
        if (have_odd) { u128_to_str(omn, omn_s); u128_to_str(omx, omx_s); }
        char ratio_s[32];
        if (prev_size) snprintf(ratio_s, sizeof(ratio_s), "%.6f", (double)ncur / prev_size);
        else snprintf(ratio_s, sizeof(ratio_s), "nan");
        printf("%4d %14zu %13s %13.4e %14.6f %8zu %8zu %10zu %10zu %10zu %24s %24s\n",
               d, ncur, ratio_s, pred, (double)ncur / pred, n_odd, ncur - n_odd,
               r0, r1, r2,
               have_odd ? omn_s : "-", have_odd ? omx_s : "-");
        printf("#LEVEL %d %zu %zu %zu %zu %zu %zu %s %s\n", d, ncur, n_odd, ncur - n_odd,
               r0, r1, r2, buf, mx_s);
        if (d <= odd_list_depth) {
            printf("#ODDS %d", d);
            for (size_t i = 0; i < ncur; i++) {
                if (cur[i] & 1) { u128_to_str(cur[i], omn_s); printf(" %s", omn_s); }
            }
            printf("\n");
        }
        reached = d;
        total_nodes += (long long)ncur;
        prev_size = ncur;

        if (d == max_depth) break;

        /* 生成下一层 */
        size_t need = (size_t)((double)ncur * 1.45) + 1024;
        if (need > cap_nxt) {
            if (need * sizeof(u128) > (size_t)(mem_guard_gb * 1e9)) {
                printf("[内存保护] 下一层预计需要 %.2f GB，超过阈值 %.1f GB，停在深度 %d。\n",
                       need * sizeof(u128) / 1e9, mem_guard_gb, d);
                goto done;
            }
            u128 *tmp = realloc(nxt, need * sizeof(u128));
            if (!tmp) { printf("[分配失败] 停在深度 %d。\n", d); goto done; }
            nxt = tmp; cap_nxt = need;
        }
        nnext = 0;
        for (size_t i = 0; i < ncur; i++) {
            u128 x = cur[i];
            u128 a = 2 * x;
            if (nnext == cap_nxt) {
                u128 *tmp = realloc(nxt, cap_nxt * 2 * sizeof(u128));
                if (!tmp) { printf("[分配失败] 停在深度 %d。\n", d); goto done; }
                nxt = tmp; cap_nxt *= 2;
            }
            nxt[nnext++] = a;
            if (x % 3 == 2) {
                u128 y = (2 * x - 1) / 3;
                if (y == 1) { collisions_skipped++; }
                else {
                    if (nnext == cap_nxt) {
                        u128 *tmp = realloc(nxt, cap_nxt * 2 * sizeof(u128));
                        if (!tmp) { printf("[分配失败] 停在深度 %d。\n", d); goto done; }
                        nxt = tmp; cap_nxt *= 2;
                    }
                    nxt[nnext++] = y;
                }
            }
        }

        if (verify) {
            qsort(cur, ncur, sizeof(u128), cmp_u128);
            qsort(nxt, nnext, sizeof(u128), cmp_u128);
            for (size_t i = 1; i < nnext; i++)
                if (nxt[i] == nxt[i - 1]) {
                    u128_to_str(nxt[i], buf);
                    printf("[校验失败] 层 %d 内有重复值 %s\n", d + 1, buf);
                    verify_fail++;
                    break;
                }
            for (size_t i = 0; i < nnext; i++) {
                u128 p = parent_of(nxt[i]);
                if (!contains(cur, ncur, p)) {
                    u128_to_str(nxt[i], buf);
                    printf("[校验失败] 节点 %s 的父节点不在上一层 %d\n", buf, d);
                    verify_fail++;
                    if (verify_fail > 5) break;
                }
            }
        }

        u128 *sw = cur; cur = nxt; nxt = sw;
        size_t sc = cap_cur; cap_cur = cap_nxt; cap_nxt = sc;
        ncur = nnext;
    }
done:;
    double t1 = now_s();
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    /* 注意：macOS 的 ru_maxrss 单位是字节，且本机实测它明显低估（见 findings 里的对照实验）；
       权威的峰值用 /usr/bin/time -l 的 peak memory footprint 读取。这里按字节换算成 MB 打印。 */
    printf("#SUMMARY reached_depth=%d total_nodes=%lld verify_fail=%d skipped_root_child=%llu "
           "seconds=%.2f getrusage_maxrss_mb=%.1f\n",
           reached, total_nodes, verify_fail, collisions_skipped, t1 - t0, ru.ru_maxrss / 1e6);
    printf("实际到达深度 = %d；累计节点数 = %lld；耗时 = %.2f s\n", reached, total_nodes, t1 - t0);
    printf("getrusage 峰值常驻内存 = %.1f MB（本机该字段低估，仅作参考；"
           "权威峰值请用 /usr/bin/time -l）\n", ru.ru_maxrss / 1e6);
    printf("本层数组的规模示意：最深一步同时驻留最后两层，各元素 16 字节（unsigned __int128）\n");
    printf("校验失败次数 = %d（0 表示每一层的层内唯一性与父节点归属均通过）\n", verify_fail);
    printf("生成到节点 1 而被跳过的次数 = %llu（应当恰为 1，来自 2 -> 1）\n", collisions_skipped);
    free(cur); free(nxt);
    return verify_fail ? 2 : 0;
}
