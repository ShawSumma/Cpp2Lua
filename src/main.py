import json
import struct

interp = True

class Compiler:
    def __init__(self, fn):
        with open('out.json') as f:
            jsontxt = f.read()
        jsonobj = json.loads(jsontxt)
        self.json = jsonobj
        self.code = []
        self.fnc = 0
        self.globalc = 0
        self.depth = 0
        self.typec = 0
        self.types = []
        self.dat = {}
        self.fmap = []
        self.exports = {}
        self.symbols = {}
        self.loadc = 0
        self.storec = 0
        self.walks = {
            'get_global': Emit.get_global,
            'set_global': Emit.set_global,
            'get_local': Emit.get_local,
            'set_local': Emit.set_local,
            'tee_local': Emit.tee_local,
            'const': Emit.const,
            'add': Emit.add,
            'neg': Emit.neg,
            'sub': Emit.sub,
            'mul': Emit.mul,
            'div': Emit.div_s,
            'div_s': Emit.div_s,
            'div_u': Emit.div_s,
            'rem': Emit.rem_s,
            'rem_s': Emit.rem_s,
            'rem_u': Emit.rem_s,
            'load': Emit.load,
            'load8_u': Emit.load,
            'load16_u': Emit.load,
            'load32_u': Emit.load,
            'load8_s': Emit.load,
            'load16_s': Emit.load,
            'load32_s': Emit.load,
            'store': Emit.store,
            'store8': Emit.store,
            'store16': Emit.store,
            'store32': Emit.store,
            'return': Emit.ret,
            'end': Emit.end,
            'drop': Emit.drop,
            'block': Emit.block,
            'loop': Emit.loop,
            'ne': Emit.ne,
            'eq': Emit.eq,
            'gt': Emit.gt_s,
            'ge': Emit.ge_s,
            'lt': Emit.lt_s,
            'le': Emit.le_s,
            'gt_s': Emit.gt_s,
            'ge_s': Emit.ge_s,
            'lt_s': Emit.lt_s,
            'le_s': Emit.le_s,
            'gt_u': Emit.gt_s,
            'ge_u': Emit.ge_s,
            'lt_u': Emit.lt_s,
            'le_u': Emit.le_s,
            'eqz': Emit.eqz,
            'and': Emit.opand,
            'xor': Emit.xor,
            'or': Emit.opor,
            'br_table': Emit.br_table,
            'br_if': Emit.br_if,
            'br': Emit.br,
            'shl': Emit.shl,
            'shr_s': Emit.shr,
            'shr_u': Emit.shr,
            'end': Emit.end,
            'select': Emit.select,
            'abs': Emit.opabs,
            'sqrt': Emit.opsqrt,
            'ceil': Emit.opciel,
            'floor': Emit.opfloor,
            'call': Emit.call,
            'call_indirect': Emit.calli,
            'demote/f32': Emit.passop,
            'demote/f64': Emit.passop,
            'promote/f32': Emit.passop,
            'promote/f64': Emit.passop,
            'trunc/f32': Emit.passop,
            'trunc/f64': Emit.passop,
            'trunc_s/f32': Emit.passop,
            'trunc_s/f64': Emit.passop,
            'trunc_s/i32': Emit.passop,
            'trunc_u/i32': Emit.passop,
            'trunc_s/i64': Emit.passop,
            'trunc_u/i64': Emit.passop,
            'extend_s/i32': Emit.passop,
            'extend_u/i32': Emit.passop,
            'extend_s/i64': Emit.passop,
            'extend_u/i64': Emit.passop,
            'convert_s/i32': Emit.passop,
            'convert_s/i64': Emit.passop,
            'convert_u/i32': Emit.passop,
            'convert_u/i64': Emit.passop,
            'wrap/i64': Emit.passop,
            'wrap/i64': Emit.passop,
            'reinterpret/i64': Emit.passop,
            'unreachable': Emit.passop,
        }
    def append(self, s):
        self.code.append('  '*self.depth + s)
    def enter(self):
        self.depth += 1
    def exit(self):
        self.depth -= 1
    def all(self):
        self.append('g = {[0]=2^24}')
        # for i in self.json:
        #     if i['name'] == 'export':
        #         for ent in i['entries']:
        #             if ent['kind'] == 'function':
        #                 si = '_' + ent['field_str']
        #                 self.append(f'local {si} = nil')
        self.walk(self.json)
        # ret = []
        # for i in self.symbols:
        #     si = '_' + self.symbols[i]
        #     self.append(f'local {si} = nil')
        mem = '{' + ', '.join(['_'+i for i in self.fmap]) +'}'
        self.append(f'local f = {mem}')
        fmtmem = '{' + ', '.join([f"[{k}]={self.dat[k]}" for k in self.dat]) + '}'
        self.append(f'mem = {fmtmem}')
        self.append('local argc = #arg')
        self.append('local argv = _libc.malloc(bigint(4 * (argc+1)))')
        self.append('for k=0, argc do')
        self.append('  local len = string.len(arg[k])')
        self.append('  local m = _libc.malloc(bigint(len+1))')
        self.append('  _memset(argv + k * 4 + 0, bit.rshift(m, 0) % 256)')
        self.append('  _memset(argv + k * 4 + 1, bit.rshift(m, 8) % 256)')
        self.append('  _memset(argv + k * 4 + 2, bit.rshift(m, 16) % 256)')
        self.append('  _memset(argv + k * 4 + 3, bit.rshift(m, 24) % 256)')
        self.append('  for k2=0, len do')
        self.append('    _memset(m+k2, string.byte(string.sub(arg[k], k2+1, k2+1)) or 0)')
        self.append('  end')
        self.append('end')
        self.append('for k,v in pairs(mem) do mem[k] = bigint(v) end')
        self.append('local stack = {argc+1, argv}')
        self.append('_main(stack)')
        self.append('os.exit(_char(stack[#stack]))')
    def walk_import(self, *ent):
        for i in ent:
            if i['kind'] == 'function':
                name = i['fieldStr']
                self.append(f'local _{name} = extern.{name}')
                self.symbols[self.fnc] = name
                self.fnc += 1
            elif i['kind'] == 'global':
                count = self.globalc
                self.append(f'g[{count}] = bigint(0)')
                self.globalc += 1
            else:
                pass
    def walk_data(self, *ent):
        for jsv in ent:
            offs = int(jsv['offset']['immediates'])
            if isinstance(jsv['data'], list):
                for pl, i in enumerate(jsv['data']):
                    self.dat[offs+pl] = i
    def walk(self, obj):
        if isinstance(obj, list):
            for i in obj:
                self.walk(i)
        else:
            name = obj['name']
            if name == 'code':
                ent = obj['entries']
                self.walk_code(*ent)
            elif name == 'import':
                ent = obj['entries']
                self.walk_import(*ent)
            elif name == 'data':
                ent = obj['entries']
                self.walk_data(*ent)
            elif name == 'type':
                for i in obj['entries']:
                    self.types.append(len(i['params']))
            elif name == 'element':
                ent = obj['entries']
                for e in ent:
                    for i in e['elements']:
                        name = self.getfname(i)
                        self.fmap.append(name)
            elif name == 'function':
                self.typemap = obj['entries']
            elif name == 'export':
                ents = obj['entries']
                for ent in ents:
                    if ent['kind'] == 'function':
                        self.exports[ent['field_str']] = ent['index']
                        self.symbols[int(ent['index'])] = ent['field_str']
            else:
                pass
    def getfname(self, name):
        name = int(name)
        if name in self.symbols:
            return self.symbols[name]
        else:
            ret = f'f{name}'
            return ret
    def walk_op(self, op):
        self.walks[op['name']](self, op)
    def walk_fn_body(self, locs, code):
        self.ends = ['']
        self.blockc = 0
        self.localc = 0
        name = self.getfname(self.fnc)
        self.append(f'_{name} = _{name} or function (stack)')
        self.enter()
        # self.append('do')
        # self.enter()
        self.append('local l = {}')
        nargc = self.types[self.typemap[self.typec]]
        for i in range(nargc)[::-1]:
            self.append(f'l[{i}] = stack[#stack]')
            self.append('stack[#stack] = nil')
        pl = 0
        for i in locs:
            for _ in range(i['count']):
                pl += 1
        for i in code:
            self.walk_op(i)
        self.exit()
        self.append('end')
        self.fnc += 1
        self.typec += 1
    def walk_code(self, *args):
        for i in args:
            self.walk_fn_body(i['locals'], i['code'])
    def get_code(self):
        return '\n'.join(self.code)


class EmitDefault(Compiler):
    def set_global(self, js):
        imm = js['immediates']
        self.append(f'g[{imm}] = stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def get_global(self, js):
        imm = js['immediates']
        self.append(f'stack[#stack+1] = g[{imm}]')

    def set_local(self, js):
        imm = js['immediates']
        self.append(f'l[{imm}] = stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def tee_local(self, js):
        imm = js['immediates']
        self.append(f'l[{imm}] = stack[#stack]')

    def get_local(self, js):
        imm = js['immediates']
        self.append(f'stack[#stack+1] = l[{imm}]')

    def block(self, js):
        self.blockc += 1
        bc = self.blockc
        self.ends.append(f'::b{bc}::')

    def loop(self, js):
        self.blockc += 1
        bc = self.blockc
        self.append(f'::b{bc}::')
        self.ends.append(None)

    def const(self, js):
        imm = js['immediates']
        if isinstance(imm, list):
            [imm] = struct.unpack('f' if len(imm) == 4 else 'd', bytes(imm))
        self.append(f'stack[#stack+1] = bigint({imm})')

    def drop(self, js):
        self.append('stack[#stack] = nil')

    def xor(self, js):
        self.append(f'stack[#stack-1] = bit.bxor(stack[#stack-1], stack[#stack] ~= bigint(0))')
        self.append(f'stack[#stack] = nil')

    def opand(self, js):
        self.append(f'stack[#stack-1] = bit.band(stack[#stack-1], stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def opor(self, js):
        self.append(f'stack[#stack-1] = bit.bor(stack[#stack-1], stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def ne(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] ~= stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def eq(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] == stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def gt_s(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] > stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def lt_s(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] < stack[#stack])')
        self.append(f'stack[#stack] = nil')
    
    def ge_s(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] >= stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def le_s(self, js):
        self.append(f'stack[#stack-1] = andor(stack[#stack-1] <= stack[#stack])')
        self.append(f'stack[#stack] = nil')
        
    def eqz(self, js):
        self.append(f'stack[#stack] = andor(stack[#stack] == bigint(0))')

    def br_if(self, js):
        imm = self.blockc - int(js['immediates'])
        self.append('do')
        self.enter()
        self.append('local case = stack[#stack]')
        self.append('stack[#stack] = nil')
        self.append(f'if case ~= bigint(0) then goto b{imm} end')
        self.exit()
        self.append('end')

    def br(self, js):
        imm = self.blockc - int(js['immediates'])
        self.append(f'goto b{imm}')

    def shr(self, js):
        self.append(f'stack[#stack-1] = bit.rshift(stack[#stack-1], stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def shl(self, js):
        self.append(f'stack[#stack-1] = bit.lshift(stack[#stack-1], stack[#stack])')
        self.append(f'stack[#stack] = nil')

    def add(self, js):
        self.append(f'stack[#stack-1] = stack[#stack-1] + stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def sub(self, js):
        self.append(f'stack[#stack-1] = stack[#stack-1] - stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def opabs(self, js):
        self.append(f'if stack[#stack] < bigint(0) then stack[#stack] = -stack[#stack] end')

    def div_s(self, js):
        self.append('do')
        self.enter()
        self.append('local val = stack[#stack-1] / stack[#stack]')    
        self.append('if val > bigint(0) then')
        self.enter()
        self.append('stack[#stack-1] = math.floor(val)')
        self.exit()
        self.append('else')
        self.enter()
        self.append('stack[#stack-1] = math.ceil(val)')
        self.exit()
        self.append('end')
        self.exit()
        self.append('end')
        self.append('stack[#stack] = nil')

    def mul(self, js):
        self.append(f'stack[#stack-1] = stack[#stack-1] * stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def rem_s(self, js):
        self.append(f'stack[#stack-1] = stack[#stack-1] % stack[#stack]')
        self.append(f'stack[#stack] = nil')

    def store(self, js):
        self.storec += 1
        imm = js['immediates']
        offs = imm['offset']
        if js['name'][-2] == '_':
            js['name'] = js['name'][:-2]
        count = int(js['return_type'][1:])/8 if js['name'] == 'store' else int(int(js['name'][5:]) / 8)
        self.append('do')
        self.enter()
        self.append('local val, addr = stack[#stack], stack[#stack-1]')
        self.append('stack[#stack] = nil')
        self.append('stack[#stack] = nil')
        for i in range(int(count)):
            of = offs+i
            i8 = i * 8
            self.append(f'_memset(addr + {of}, bit.rshift(val, {i8}) % 256)')
        self.exit()
        self.append('end')

    def load(self, js):
        self.loadc += 1
        imm = js['immediates']
        offs = imm['offset']
        if js['name'][-2] == '_':
            js['name'] = js['name'][:-2]
        count = int(js['return_type'][1:])/8 if js['name'] == 'load' else int(int(js['name'][4:]) / 8)
        self.append('do')
        self.enter()
        self.append('local val, addr = bigint(0), stack[#stack]')
        self.append('stack[#stack] = nil')
        for i in range(int(count)):
            of = offs+i
            i8 = i * 8
            self.append(f'val = val + bit.lshift(_memget(addr + {of}), {i8})')
        self.append('stack[#stack+1] = val')
        self.exit()
        self.append('end')

    def call(self, js):
        imm = js['immediates']
        name = self.getfname(imm)
        self.append(f'_{name}(stack)')

    def calli(self, js):
        self.append('do')
        self.enter()
        self.append('local fn = f[stack[#stack]:conv()]')
        self.append('stack[#stack] = nil')
        self.append('fn(stack)')
        self.exit()
        self.append('end')

    def ret(self, js):
        self.append('do return end')

    def end(self, js):
        val = self.ends.pop()
        if val is not None and len(val.strip()) != 0:
            self.append(val)

    def select(self, js):
        self.append('if stack[#stack-2] == bigint(0) then stack[#stack-2] = stack[#stack] else stack[#stack-2] = stack[#stack-1] end')
        self.append('stack[#stack] = nil')
        self.append('stack[#stack] = nil')

    def passop(self, js):
        pass

    def br_table(self, js):
        targ = js['immediates']['targets']
        self.append('do')
        self.enter()
        self.append(f'local val = stack[#stack]')
        self.append(f'stack[#stack] = nil')
        for pl, i in enumerate(targ):
            gt = self.blockc - i
            self.append(f'if val == bigint({pl}) then')
            self.enter()
            self.append(f'goto b{gt}')
            self.exit() 
            self.append('end')
        self.exit()
        self.append('end')

    def opciel(self, js):
        self.append('stack[#stack] = math.ceil(stack[#stack])')

    def opfloor(self, js):
        self.append('stack[#stack] = math.floor(stack[#stack])')

    def opsqrt(self, js):
        self.append('stack[#stack] = math.sqrt(stack[#stack])')

    def neg(self, js):
        self.append('stack[#stack] = -stack[#stack]')

Emit = EmitDefault

cc = Compiler('out.json')
cc.all()
with open('out.lua', 'w') as f:
    with open('src/pre.lua') as d:
        c = d.read()
    f.write(c)
    f.write('\n')
    f.write(cc.get_code())