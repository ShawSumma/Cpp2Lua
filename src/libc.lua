local bigint = require("src.bigint")

local ret = {}
local libc = {}
local allocs = {}
local news = {}
local blocks = {}
local enbuf = bigint(0)

local fdescs = {
    [0]=io.stdin,
    [1]=io.stdout,
    [2]=io.stderr,
}

local unpack = unpack or table.unpack

function ret._memget(n)
    local got = mem[ret._addr(n)] or 0
    -- assert(got)
    return got
end
local _memget = ret._memget

function ret._memset(n, v)
    mem[ret._addr(n)] = bigint(v)
end
local _memset = ret._memset

local function readstr(addr)
    local tab = {}
    while _memget(addr) ~= bigint(0) do
        tab[#tab+1] = string.char(_memget(addr))
        addr = addr+1
    end
    return table.concat(tab)
end

local function setenbuf(str)
    local len = string.len(str)
    libc.free(enbuf)
    enbuf = libc.malloc(bigint(len+1))
    -- for i=addr, string.len(str)
    for i=0, len-1 do
        local chr = string.sub(str, i+1, i+1)
        local byte = string.byte(chr)
        _memset(enbuf + i, bigint(byte))
    end
    _memset(enbuf+len+1, bigint(0))
end

function ret._addr(n)
    if type(n) ~= 'table' then
        return n
    else
        local ret = n:conv()
        return ret
    end
end
local _addr = ret._addr

function ret._char(n)
    return ret._addr(n) % 256
end
local _char = ret._char

function ret.clean(ptr)
    ptr = ret._addr(ptr)
    if ptr == 0 then
        return true
    end
    for k,v in pairs(allocs) do
        if ret._addr(k) == ptr then
            return true
        end
    end
    return false
end

function ret.allocated(ptr)
    for k,v in pairs(allocs) do
        if ret._addr(k) <= ptr and ret._addr(k+v) > ptr then
            return true
        end
    end
    return false
end

function ret._offsize(ptr)
    for k,v in pairs(allocs) do
        if k <= ptr and k+v > ptr then
            local tab = {}
            for i=k, k+v do
                tab[#tab+1] = _memget(i)
            end
            return tab
        end
    end
    assert(0)
end
    
function libc.time()
    return bigint(os.time())
end

function libc.malloc(size)
    if #blocks == 0 then
        blocks = {{2^24+1, 2^32-2^24-1}}
    end
    local count = 0
    for k, v in ipairs(blocks) do
        local pl = v[1]
        if bigint(v[2]) >= size then
            allocs[pl] = size
            blocks[k][1] = v[1] + size
            blocks[k][2] = v[2] - size
            return pl
        end
    end
    print('alloc failed')
    os.exit(1)
end

function libc.free(ptr)
    if ret._addr(ptr) == 0 then
        return
    end
    assert(clean(ptr))
    local size = allocs[ptr]
    local eptr = size + ptr
    for k, v in ipairs(blocks) do
        if bigint(v[1]) == eptr then
            v[1] = v[1] - size
            v[2] = v[2] + size
            allocs[ptr] = nil
            return
        end
    end
    local count = 0
    for _ in ipairs(allocs) do
        count = count + 1
    end
    allocs[ptr] = nil
    blocks[#blocks+1] = {ptr, size}
end

function libc.puts(ptr)
    while _memget(ptr) ~= bigint(0) do
        io.write(string.char(_memget(ptr)))
        ptr = ptr+1
    end
    io.write('\n')
    return bigint(0)
end

function libc.realloc(ptr, size)
    if ret._addr(ptr) == 0 then
        return libc.malloc(size)
    end
    local ret = libc.malloc(size)
    for i=0, size-1 do
        _memset(ret + i, _memget(ptr + i))
    end 
    libc.free(ptr)
    return ret
end

function libc.abort() 
    os.exit(1)
end

function libc.abs(n)
    if n < bigint(0) then
        return -n
    end
    return n
end

function libc.acos(n)
    return math.acos(n)
end

function libc.asin(n)
    return math.asin(n)
end

function libc.atan(n)
    return math.atan(n)
end

function libc.atan2(a, b)
    return math.atan(a, b)
end

function libc.cos(n)
    return math.cos(n)
end

function libc.cosh(n)
    return math.cosh(n)
end

function libc.sin(n)
    return math.sin(n)
end

function libc.sinh(n)
    return math.sinh(n)
end

function libc.tan(n)
    return math.tan(n)
end

function libc.tanh(n)
    return math.tanh(n)
end

function libc.exp(n)
    return 2.7182818284590452353602874713526 ^ n
end

function libc.getenv(ptr)
    local name = readstr(ptr)
    local str = os.getenv(name)
    if not str then
        setenbuf('')
        return bigint(0)
    end
    setenbuf(str)
    return enbuf
end

function ret.getenv(stack)
    stack[#stack] = bigint(libc.getenv(stack[#stack]))
end

function ret.malloc(stack)
    local size = stack[#stack]
    stack[#stack] = bigint(libc.malloc(size))
end

function ret.free(stack)
    local ptr = stack[#stack]
    stack[#stack] = nil
    libc.free(ptr)
end

function ret.realloc(stack)
    local size = stack[#stack]
    stack[#stack] = nil
    stack[#stack] = bigint(libc.realloc(stack[#stack], size))
end

function ret.time(stack)
    stack[#stack] = libc.time()
end

function ret.puts(stack)
    local ptr = stack[#stack]
    stack[#stack] = bigint(0);
    while _memget(ptr) ~= bigint(0) do
        io.write(string.char(_char(_memget(ptr))))
    ptr = ptr+1
    end
    io.write('\n')
end

function ret.putchar(stack)
    local chr = _char(stack[#stack])
    io.write(string.char(chr))
    stack[#stack] = nil
end

function ret.__printn(stack)
    print('debug: ' .. tostring(stack[#stack]))
    -- stack[#stack] = nil
end

function ret.getchar(stack)
    local ret = string.byte(io.read(1))
    stack[#stack+1] = bigint(ret)
end

function ret.putc(stack)
    local fdec = _addr(stack[#stack])
    local file
    if fdec == 0 then
        file = io.stdout
    else
        file = fdescs[fdec]
    end
    stack[#stack] = nil
    local bigchr = _char(stack[#stack])   
    local chr = string.char(bigchr)
    file:write(chr)
    stack[#stack] = bigchr
end

function ret.getc(stack)
    local fdec = _addr(stack[#stack])
    local file
    if fdec == 0 then
        file = io.stdin
    else
        file = fdescs[fdec]
    end
    local chr = file:read(1)
    if chr then
        local byte = string.byte(chr)
        stack[#stack] = bigint(byte)
    else
        stack[#stack] = bigint(-1)
    end
end

ret._IO_putc = ret.putc
ret._IO_getc = ret.getc

local function andor(x)
    if x then
        return bigint(1)
    else
        return bigint(0)
    end
end

return {ret=ret, libc=libc, andor=andor}
