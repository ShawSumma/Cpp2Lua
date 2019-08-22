rm out.lua
./cc.sh -O3 test/retfib.cpp
echo
echo 'LuaJIT cc=3 lua=3'
/usr/bin/time -f "%e"  luajit -O3 out.lua
echo  
echo 'LuaJIT cc=3 lua=0'
/usr/bin/time -f "%e"  luajit -O0 out.lua
echo  
echo 'Lua5.3 cc=3 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo  
echo 'Lua5.2 cc=3'
/usr/bin/time -f "%e"  lua5.2 out.lua

rm out.lua
./cc.sh -O2 test/retfib.cpp
echo  
echo 'LuaJIT cc=2 lua=3'
/usr/bin/time -f "%e"  luajit -O3 out.lua
echo  
echo 'LuaJIT cc=2 lua=0'
/usr/bin/time -f "%e"  luajit -O0 out.lua
echo  
echo 'Lua5.3 cc=2 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo  
echo 'Lua5.2 cc=2'
/usr/bin/time -f "%e"  lua5.2 out.lua

rm out.lua
./cc.sh -O1 test/retfib.cpp
echo  
echo 'LuaJIT cc=1 lua=3'
/usr/bin/time -f "%e"  luajit -O3 out.lua
echo  
echo 'LuaJIT cc=1 lua=0'
/usr/bin/time -f "%e"  luajit -O0 out.lua
echo  
echo 'Lua5.3 cc=1 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo  
echo 'Lua5.2 cc=1'
/usr/bin/time -f "%e"  lua5.2 out.lua

rm out.lua
./cc.sh -O0 test/retfib.cpp
echo  
echo 'LuaJIT cc=0 lua=3'
/usr/bin/time -f "%e"  luajit -O3 out.lua | grep "real"
echo  
echo 'LuaJIT cc=0 lua=0'
/usr/bin/time -f "%e"  luajit -O0 out.lua
echo  
echo 'Lua5.3 cc=0 '
/usr/bin/time -f "%e"  lua5.3 out.lua
echo  
echo 'Lua5.2 cc=0'
/usr/bin/time -f "%e"  lua5.2 out.lua
