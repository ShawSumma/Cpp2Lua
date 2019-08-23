#include <lua/functional>
#include <lua/vector>
#include <lua/io>

int main() {
    std::function<long(long, long)> add;
    add = [&](long x, long y) -> long{
        if (x == 0) {
            return y;
        }
        return add(x-1, y+1);
    };
    std::println(add(10, 15));
}