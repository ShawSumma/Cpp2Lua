clang++-8 -std=c++17 $@ --target=wasm32 -c -o out.wasm -I. -DLUA_CPP_COMPILER &&
    wasm2json out.wasm -o out.json > out.json &&
    # wasm2wat out.wasm -o out.wasm &&
    python3 main.py &&
    luamin -f out.lua > out.min.lua