#include <lua/io>
#include <lua/vector>
#include <lua/memory>

void dostuff() {
    lua::auto_ptr<int> x = new int(10);
    lua::vector<lua::auto_ptr<int>> vec;
    vec.push_back(x);
    *x += 1;
    vec.push_back(x);
    lua::println(*vec[1]);
}

int main(void) {
    dostuff();
    lua::println(lua::interp::allocs());
}