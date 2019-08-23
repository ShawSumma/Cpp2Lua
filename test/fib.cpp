#include <lua/io>

using namespace std;

namespace bench {
    int fib(int x) {
        if (x < 2) {
            return x;
        }
        return fib(x-2) + fib(x-1);
    }
}

int main(void) {
    return bench::fib(35);
}