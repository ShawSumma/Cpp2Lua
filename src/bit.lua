--[[
  (c) 2008-2011 David Manura.  Licensed under the same terms as Lua (MIT).
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
  (end license)
--]]

local bigint = require("src.bigint")

local ret = {}

local big0 = bigint(0)

local M = {}

local function floor(n)
  return n - n % 1
end

local function pow2(n)
  n = bigint(n)
  local ret = bigint(1)
  while n > big0 do
    ret = ret*2
    n = n-1
  end
  return ret
end

local function pow16(n)
  n = bigint(n)
  local ret = bigint(1)
  while n > big0 do
    ret = ret*16
    n = n-1
  end
  return ret
end

-- local function memoize(f)
--   local mt = {}
--   local t = setmetatable({}, mt)
--   function mt:__index(k)
--     local v = f(k); t[_addr(k)] = v
--     return v
--   end
--   return t
-- end

-- local function make_bitop(fn, name)
--   -- m = bigint(m)
--   local function bitop(a, b)
--     print(a, b)
--     a, b = bigint(a), bigint(b)
--     local ret = big0
--     while not (a == big0 and b == big0) do
--       ret = ret * 2
--       if fn(a % 2, b % 2) then
--         ret = ret + 1
--       end
--       a = b32.rshfit(a, 1)
--       b = b32.rshift(b, 1)
--     end
--     return ret
--   end
--   return bitop
-- end

-- ret.bxor = make_bitop (function (a, b) return (a ~= big0) ~= (b ~= big0) end, 'xor')
-- local bxor = ret.bxor

-- ret.bor = make_bitop (function (a, b) return a ~= big0 or b ~= big0 end, 'or')
-- local bor = ret.bor

-- ret.bnot = make_bitop (function (a, b) return a == big0 end, 'not')
-- local bnot = ret.bnot

-- ret.bxor = make_bitop (function (a, b) return (a ~= big0) and (b ~= big0) end, 'xor')
-- local band = ret.band

-- local lshift, rshift -- forward declare

function rshift(a,disp) -- Lua5.2 insipred
  if bigint(disp) < big0 then return lshift(a,-disp) end
  if bigint(disp) == big0 then return a end
  return floor(a / pow2(disp))
end
ret.rshift = rshift

local function lshift(a,disp) -- Lua5.2 inspired
  if bigint(disp) < big0 then return rshift(a,-disp) end
  if bigint(disp) == big0 then return a end
  return (a * pow2(disp))
end
ret.lshift = lshift

-- function ret.tohex(x, n) -- BitOp style
--   n = n or 8
--   local up
--   if n <= big0 then
--     if n == big0 then return '' end
--     up = true
--     n = - n
--   end
--   x = band(x, pow16(n)-1)
--   return ('%0'..n..(up and 'X' or 'x')):format(x)
-- end
-- local tohex = ret.tohex

-- function ret.extract(n, field, width) -- Lua5.2 inspired
--   width = width or 1
--   return band(rshift(n, field), 2^width-1)
-- end
-- local extract = ret.extract

-- function ret.replace(n, v, field, width) -- Lua5.2 inspired
--   width = width or 1
--   local mask1 = 2^width-1
--   v = band(v, mask1) -- required by spec?
--   local mask = bnot(lshift(mask1, field))
--   return band(n, mask) + lshift(v, field)
-- end
-- local replace = ret.replace

-- function ret.bswap(x)  -- BitOp style
--   local a = band(x, 0xff)
--   x = rshift(x, 8)
--   local b = band(x, 0xff)
--   x = rshift(x, 8)
--   local c = band(x, 0xff)
--   x = rshift(x, 8)
--   local d = band(x, 0xff)
--   return lshift(lshift(lshift(a, 8) + b, 8) + c, 8) + d
-- end
-- local bswap = ret.bswap

-- function ret.rrotate(x, disp)  -- Lua5.2 inspired
--   disp = disp % 32
--   local low = band(x, pow2(disp)-1)
--   return rshift(x, disp) + lshift(low, 32-disp)
-- end
-- local rrotate = ret.rrotate

-- function ret.lrotate(x, disp)  -- Lua5.2 inspired
--   return rrotate(x, -disp)
-- end
-- local lrotate = ret.lrotate

-- ret.rol = ret.lrotate  -- LuaOp inspired
-- ret.ror = ret.rrotate  -- LuaOp insipred
--
-- Start Lua 5.2 "bit32" compat section.
--

-- https://stackoverflow.com/questions/5977654/lua-bitwise-logical-operations

function ret.bxor(a,b)
  a,b = bigint(a), bigint(b)
  local p,c=bigint(1),bigint(0)
  while a>big0 and b>big0 do
      local ra,rb=a%2,b%2
      if ra~=rb then c=c+p end
      a,b,p=(a-ra)/2,(b-rb)/2,p*2
  end
  if a<b then a=b end
  while a>big0 do
      local ra=a%2
      if ra>big0 then c=c+p end
      a,p=(a-ra)/2,p*2
  end
  return c
end

function ret.bor(a,b)
  a,b = bigint(a), bigint(b)
  local p,c=bigint(1),bigint(0)
  while a+b>big0 do
      local ra,rb=a%2,b%2
      if ra+rb>big0 then c=c+p end
      a,b,p=(a-ra)/2,(b-rb)/2,p*2
  end
  return c
end

function ret.bnot(n)
  n = bigint(n)
  local p,c=bigint(1),bigint(0)
  while n>big0 do
      local r=n%2
      if r<bigint(1) then c=c+p end
      n,p=(n-r)/2,p*2
  end
  return c
end

function ret.band(a,b)
  a,b = bigint(a), bigint(b)
  local p,c=bigint(1),bigint(0)
  while a>big0 and b>big0 do
      local ra,rb=a%2,b%2
      if ra+rb>bigint(1) then c=c+p end
      a,b,p=(a-ra)/2,(b-rb)/2,p*2
  end
  return c
end

-- function ret.lrotate(x, disp)
--   return lrotate(x , disp)
-- end

-- function ret.rrotate(x, disp)
--   return rrotate(x , disp)
-- end

-- function ret.lshift(x,disp)
--   return lshift(x, disp)
-- end

-- function ret.rshift(x,disp)
--   return rshift(x, disp)
-- end

-- function ret.extract(x, field, ...)
--   local width = ... or 1
--   return extract(x, field, ...)
-- end

-- function ret.replace(x, v, field, ...)
--   local width = ... or 1
--   return replace(x, v, field, ...)
-- end

-- local bit32 = ret
-- for k,v in pairs(bit32) do
--   ret[k] = v
-- end

-- function ret.lshift(x, d)
--   return bit32.lshift(bigint(x), bigint(d))
-- end

-- function ret.rshift(x, d)
--   return bit32.rshift(bigint(x), bigint(d))
-- end

-- function ret.band(a, b)
--   return bit32.band(bigint(a), bigint(b))
-- end

-- function ret.bor(a, b)
--   return bit32.bor(bigint(a), bigint(b))
-- end

-- function ret.bxor(a, b)
--   return bit32.bxor(bigint(a), bigint(b))
-- end

-- function ret.bnot(a)
--   return bit32.bnot(bigint(a))
-- end

return {bit32=ret}