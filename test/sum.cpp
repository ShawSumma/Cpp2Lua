#include <lua/io>
#include <lua/vector>
#include <lua/memory>

class number {
    double _num;
public:
    number(double d) {
        _num = d;
    }
    operator double() {
        return _num;
    }
    number operator +=(number num) {
        _num += num._num;
        return _num;
    }
};

template<typename T=long>
T sum_simple(T num) {
    std::vector<size_t> vec;
    for (size_t i = 1; i <= num; i++) {
        vec.push_back(i);
    }
    size_t val = 0;
    for (auto &i: vec) {
        val += i;
    }
    return val;
}

template<typename T=long>
T sum_numeric(size_t num) {
    std::vector<size_t> vec{num+1};
    std::itoa(vec.begin(), vec.end(), 0);
    return std::accumulate(vec.begin(), vec.end(), 0);
}

int main(void) {
    std::println(sum_simple(10));
    std::println(sum_numeric(10));
    std::println(std::lua::allocs());
}