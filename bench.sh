rm out.lua
./cc.sh -O3 $1 &> /dev/null
echo
echo 'Clang -O3 LuaJIT -O3'
/usr/bin/time -f "%e"  luajit -O3 out.lua
echo
echo 'Clang -O3 Lua5.3 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo
echo 'Clang -O3 Lua5.2'
/usr/bin/time -f "%e"  lua5.2 out.lua
./cc.sh -O0 $1 &> /dev/null
echo
echo 'Clang -O0 LuaJIT -O3'
/usr/bin/time -f "%e"  luajit -O3 out.lua
echo
echo 'Clang -O0 Lua5.3 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo
echo 'Clang -O0 Lua5.2'
/usr/bin/time -f "%e"  lua5.2 out.lua
