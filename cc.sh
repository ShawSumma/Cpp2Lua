clang++-8 -std=c++17 $@ --target=wasm32 -c -o out.wasm -I. &&
    wasm2json out.wasm -o out.json > out.json &&
    wasm2wat out.wasm -o out.wasm
    python3 main.py