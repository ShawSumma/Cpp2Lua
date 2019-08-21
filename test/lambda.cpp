#include <lua/io>

using namespace lua;

template <typename T>
T fib(T n) {
    if (n < 2) {
        return n;
    }
    return fib<T>(n-2) + fib<T>(n-1);
}

template <typename T>
auto math(T a) {
    return [=](T b) {
        return [=](T c) {
            return [=](T d) -> T {
                return a * b + c * d;
            };
        };
    };
}

int main() {
    int arr[2][2] = {
        {fib(6), fib(3)},
        {fib(5), fib(10)}
    };
    auto val = math<long>(arr[0][0])(arr[0][1])(arr[1][0])(arr[1][1]);
    println(val);
    return 0;
}