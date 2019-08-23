clang++-8 -std=c++17 $@ --target=wasm32 -c -o out.wasm -I. -DLUA_CPP_COMPILER &&
wasm2json out.wasm -o out.json > out.json &&
python3 src/main.py