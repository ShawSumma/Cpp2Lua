#include <stdio.h>
#include <stdbool.h>

void *__printn(void *);

#ifndef LUA_COMPILER
void *__printn(void *vval) {
    printf("debug: %ld\n", vval);
}
#endif

bool is_prime(int x) {
    for(int i = 2; i < x; i++) {
        if(x % i == 0) {
            return 0;
        }
    }
    return 1;
}

int main() {
    int val = 2;
    long sum = 0;
    while (true) {
        if (is_prime(val)) {
            sum += val;
        }
        val ++;
        if (val == 5000) break;
    }
    __printn(sum);
}