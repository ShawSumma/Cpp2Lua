clang-8 -std=gnu99 $@ --target=wasm32 -c -o out.wasm -DLUA_COMPILER &&
    wasm2wat out.wasm -o out.wat &&
    wasm-ld-8 out.wasm -o out.wasm --allow-undefined --no-entry \
        --export-all &&
    wasm2json out.wasm -o out.json > out.json &&
    python3 src/main.py &&
    luamin -f out.lua > out.min.lua &&
    echo "Compiled Successfully"