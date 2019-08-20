#include <lua/io>

namespace bench {
    int fib(int x) {
        if (x < 2) {
            return x;
        } 
        return fib(x-2) + fib(x-1);
    }
}

int main(void) {
    lua::println(bench::fib(35));
}