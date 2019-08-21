#include <lua/io>

using namespace lua;

namespace bench {
    int fib(int x) {
        if (x < 2) {
            return x;
        }
        return fib(x-2) + fib(x-1);
    }
}

int main(void) {
    println(bench::fib(33));
}