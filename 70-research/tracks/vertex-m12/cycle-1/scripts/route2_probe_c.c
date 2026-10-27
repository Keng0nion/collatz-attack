/* 探针 C：pthread 分片 + 原子计数器 + 大缓冲 + fwrite + 互斥锁 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <gmp.h>

static volatile long long NextChunk = 0;
static long long NChunks = 1000;
static unsigned char *Dec = NULL;
static long long Total = 5000000;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static long long NCands = 0;
static mpq_t *Cands = NULL;

typedef struct {
    int tid;
    long long n;
} work_t;

static long long now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static void *worker(void *arg)
{
    work_t *w = (work_t *)arg;
    for (;;) {
        long long cid = __sync_fetch_and_add(&NextChunk, 1);
        if (cid >= NChunks)
            break;
        long long lo = cid * 5000;
        long long hi = lo + 5000;
        if (hi > Total)
            hi = Total;
        for (long long i = lo; i < hi; i++)
            Dec[i] = (unsigned char)('S' + (i % 3));
        pthread_mutex_lock(&mu);
        NCands++;
        if (Cands) {
            mpq_set_ui(Cands[0], cid, 1);
        }
        pthread_mutex_unlock(&mu);
        w->n += hi - lo;
    }
    return NULL;
}

int main(void)
{
    Dec = (unsigned char *)malloc((size_t)Total);
    if (!Dec)
        return 4;
    memset(Dec, '?', (size_t)Total);
    Cands = (mpq_t *)malloc(sizeof(mpq_t) * 16);
    if (!Cands)
        return 4;
    for (int i = 0; i < 16; i++)
        mpq_init(Cands[i]);
    pthread_t th[8];
    work_t ws[8];
    long long t0 = now_ns();
    for (int t = 0; t < 8; t++) {
        ws[t].tid = t;
        ws[t].n = 0;
        if (pthread_create(&th[t], NULL, worker, &ws[t]) != 0)
            return 4;
    }
    for (int t = 0; t < 8; t++)
        pthread_join(th[t], NULL);
    long long dt = now_ns() - t0;
    FILE *f = fopen("route2_probe_c_out.bin", "wb");
    if (!f)
        return 4;
    size_t wr = fwrite(Dec, 1, (size_t)Total, f);
    fclose(f);
    printf("wr=%zu dt_ns=%lld ncands=%lld\n", wr, dt, NCands);
    return 0;
}
