extern = {}
mem = {}

if not bit then
  bit = {
    lshift = bit32.lshift,
    rshift = bit32.rshift
  }
end
function extern.printn(stack)
  print(stack[#stack])
  stack[#stack] = nil
end

function extern.memdump(stack)
  print(table.unpack(mem))
end

function extern.newline(stack)
  print()
end

function extern.println(stack)
  local ind = stack[#stack]
  while mem[ind] ~= 0 do
    io.write(string.char(mem[ind]))
    ind = ind + 1
  end
  io.write('\n')
  stack[#stack] = nil
end

function extern.putchar(stack)
  io.write(string.char(stack[#stack]))
  -- print('out: ' .. tostring(stack[#stack]))
  stack[#stack] = nil
end

function _store(storage, offs)
  storage[offs] = val
end

function _load(storage, offs)
  return storage[offs]
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