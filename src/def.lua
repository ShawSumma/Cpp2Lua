extern = {}
mem = {}
stackend = 2^16
allocs = {}
news = {}
blocks = {{stackend+1, 2^32-2^16-1}}

unpack = unpack or table.unpack

if not bit then
    bit = bit32
end

function extern._allocs(stack)
    local count = 0
	for _ in ipairs(allocs) do
		count = count + 1
	end
	stack[#stack+1] = count
end

function extern._blocks(stack)
    local count = 0
    for _ in ipairs(blocks) do
        count = count + 1
    end
    stack[#stack+1] = count
end

function extern._Znwm(stack)
    extern.malloc(stack)
end

function extern._Znam(stack)
    extern.malloc(stack)
end

function extern._Znaj(stack)
    extern.malloc(stack)
end

function extern._ZdlPv(stack)
    extern.free(stack)
end

function extern._ZdaPv(stack)
    extern.free(stack)
end

function extern.malloc(stack)
    local size = stack[#stack]
    stack[#stack] = nil
    local count = 0
    for k, v in ipairs(blocks) do
        local pl = v[1]
        if v[2] >= size then
            allocs[pl] = size
            blocks[k][1] = v[1] + size
            blocks[k][2] = v[2] - size
            stack[#stack+1] = pl
            return
        end
    end
    print('alloc failed')
    os.exit(1)
end

function extern.free(stack)
    local ptr = stack[#stack]
    stack[#stack] = nil
    if ptr == 0 then
        return
    end
    local size = allocs[ptr]
    local eptr = size + ptr
    for k, v in ipairs(blocks) do
        if v[1] == eptr then
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

function extern.putchar(stack)
    io.write(string.char(stack[#stack]))
    stack[#stack] = nil
end

function _num(v)
    if v then
        return 1
    else
        return 0
    end
end

function _bool(v)
    return v ~= 0
end

-- code