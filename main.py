import json
import struct

def set_global(self, js):
    imm = js['immediates']
    self.append(f'g{imm} = stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('set', f'g{imm}')

def get_global(self, js):
    imm = js['immediates']
    self.append(f'stack[#stack+1] = g{imm}')
    self.tape_append('push', f'g{imm}')

def set_local(self, js):
    imm = js['immediates']
    self.append(f'l{imm} = stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('set', f'l{imm}')

def tee_local(self, js):
    imm = js['immediates']
    self.tape_append('tee', 'local')
    self.append(f'l{imm} = stack[#stack]')
    self.tape_append('push', f'g{imm}')

def get_local(self, js):
    imm = js['immediates']
    self.append(f'stack[#stack+1] = l{imm}')

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
    self.append(f'stack[#stack+1] = {imm}')
    self.tape_append('push', f'{imm}')

def drop(self, js):
    self.append('stack[#stack] = nil')
    self.tape_append('pop')

def opand(self, js):
    self.append(f'stack[#stack-1] = _num(_bool(stack[#stack-1]) and _bool(stack[#stack]))')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', 'and')

def opor(self, js):
    self.append(f'stack[#stack-1] = _num(_bool(stack[#stack-1]) or _bool(stack[#stack]))')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', 'or')

def ne(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] ~= stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '!=')

def eq(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] == stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '==')

def gt_s(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] > stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '>')

def lt_s(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] < stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '<')
   
def ge_s(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] >= stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '>=')

def le_s(self, js):
    self.append(f'stack[#stack-1] = _num(stack[#stack-1] <= stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '<=')
    
def eqz(self, js):
    self.append(f'stack[#stack] = _num(stack[#stack] == 0)')
    self.tape_append('binop', '0')

def br_if(self, js):
    imm = self.blockc - int(js['immediates'])
    self.append('local case = stack[#stack]')
    self.append('stack[#stack] = nil')
    self.append(f'if _bool(case) then goto b{imm} end')
    self.tape_append('branch', 'if')

def br(self, js):
    imm = self.blockc - int(js['immediates'])
    self.append(f'goto b{imm}')
    self.tape_append('branch', 'const')

def shr(self, js):
    self.append(f'stack[#stack-1] = bit.rshift(stack[#stack-1], stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '>>')

def shl(self, js):
    self.append(f'stack[#stack-1] = bit.lshift(stack[#stack-1], stack[#stack])')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '<<')

def add(self, js):
    self.append(f'stack[#stack-1] = stack[#stack-1] + stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '+')

def sub(self, js):
    self.append(f'stack[#stack-1] = stack[#stack-1] - stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('binop', '-')

def opabs(self, js):
    self.append(f'if stack[#stack] < 0 then stack[#stack] = -stack[#stack] end')
    self.tape_append('call', 'abs')

def div_s(self, js):
    self.append('local val = stack[#stack-1] / stack[#stack]')    
    self.append('if val > 0 then')
    self.enter()
    self.append('stack[#stack-1] = math.floor(val)')
    self.exit()
    self.append('else')
    self.enter()
    self.append('stack[#stack-1] = math.ceil(val)')
    self.exit()
    self.append('end')
    self.append('stack[#stack] = nil')
    self.tape_append('op', '/')

def mul(self, js):
    self.append(f'stack[#stack-1] = stack[#stack-1] * stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('op', '*')

def rem_s(self, js):
    self.append(f'stack[#stack-1] = stack[#stack-1] % stack[#stack]')
    self.append(f'stack[#stack] = nil')
    self.tape_append('op', '%')

def store(self, js):
    imm = js['immediates']
    offs = imm['offset']
    if js['name'][-2] == '_':
        js['name'] = js['name'][:-2]
    count = int(js['return_type'][1:])/8 if js['name'] == 'store' else int(int(js['name'][5:]) / 8)
    self.append('local val, addr = stack[#stack], stack[#stack-1]')
    self.append('stack[#stack] = nil')
    self.append('stack[#stack] = nil')
    for i in range(int(count)):
        of = offs+i
        if count > 4:
            i1 = i + 1
            self.append(f'mem[addr + {of} + 1] = val[{i1}]')
        else:
            i8 = i * 8
            self.append(f'mem[addr + {of} + 1] = bit.rshift(val, {i8}) % 256')
    self.tape_append('mem', 'store', count=count, offset=offs)

def load(self, js):
    imm = js['immediates']
    offs = imm['offset']
    if js['name'][-2] == '_':
        js['name'] = js['name'][:-2]
    count = int(js['return_type'][1:])/8 if js['name'] == 'load' else int(int(js['name'][4:]) / 8)
    n1, n = self.request(2)
    if count > 4:
        self.append('local val, addr = {}, ' + f' {n}')
    else:
        self.append(f'local val, addr = 0, {n}')
    self.append('stack[#stack] = nil')
    self.destroy(n)
    for i in range(int(count)):
        of = offs+i
        i8 = i * 8
        if count > 4:
            i1 = i + 1
            self.append(f'val[{i1}] = mem[addr + {of} + 1]')
        else:
            self.append(f'val = val + bit.lshift(mem[addr + {of} + 1], {i8})')
    self.append('stack[#stack+1] = val')
    self.tape_append('mem', 'load', count=count, offset=offs)

def call(self, js):
    imm = js['immediates']
    self.append(f'f{imm}(stack)')
    self.tape_append('call')

def calli(self, js):
    n = self.request(1)
    self.append('local fn = f[{n}]')
    # self.append('stack[#stack] = nil')
    self.append('fn(stack)')
    self.tape_append('call')

def ret(self, js):
    self.append('do return end')
    self.tape_append('return')

def end(self, js):
    val = self.ends.pop()
    if val is not None and len(val.strip()) != 0:
        self.append(val)

def select(self, js):
    n2, n1, n = self.request(3)
    self.append('if {n2} == 0 then {n2} = {n} else {n2} = {n1} end')
    self.destroy(n1, n)
    self.tape_append('select')

def passop(self, js):
    pass

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
        self.walks = {
            'get_global': get_global,
            'set_global': set_global,
            'get_local': get_local,
            'set_local': set_local,
            'tee_local': tee_local,
            'const': const,
            'add': add,
            'sub': sub,
            'mul': mul,
            'div_s': div_s,
            'div_u': div_s,
            'rem_s': rem_s,
            'rem_u': rem_s,
            'load': load,
            'load8_u': load,
            'load16_u': load,
            'store': store,
            'store8': store,
            'store16': store,
            'return': ret,
            'end': end,
            'drop': drop,
            'block': block,
            'loop': loop,
            'ne': ne,
            'eq': eq,
            'gt': gt_s,
            'ge': ge_s,
            'lt': lt_s,
            'le': le_s,
            'gt_s': gt_s,
            'ge_s': ge_s,
            'lt_s': lt_s,
            'le_s': le_s,
            'gt_u': gt_s,
            'ge_u': ge_s,
            'lt_u': lt_s,
            'le_u': le_s,
            'eqz': eqz,
            'and': opand,
            'or': opor,
            'br_if': br_if,
            'br': br,
            'shl': shl,
            'shr_s': shr,
            'shr_u': shr,
            'end': end,
            'select': select,
            'abs': opabs,
            'call': call,
            'call_indirect': calli,
            'trunc/f32': passop,
            'trunc_s/f32': passop,
            'extend_s/i32': passop,
            'extend_u/i32': passop,
            'wrap/i64': passop,
            'unreachable': passop,
        }
    def append(self, s):
        self.code.append('  '*self.depth + s)
    def enter(self):
        self.depth += 1
    def exit(self):
        self.depth -= 1
    def all(self):
        self.walk(self.json)
        self.append(f'g0 = stackend')
        mem = '{' + ', '.join([f'[{i}]=f{i}' for i in range(0, self.fnc)]) +'}'
        self.append(f'f = {mem}')
        self.append('f%s({0, 0})' % (str(self.fnc-1), ))
    def walk_import(self, *ent):
        for i in ent:
            if i['kind'] == 'function':
                name = i['fieldStr']
                fnc = self.fnc
                self.append(f'f{fnc} = extern.{name}')
                self.fnc += 1
            elif i['kind'] == 'global':
                count = self.globalc
                self.append(f'g{count} = 0')
                self.globalc += 1
            else:
                pass
    def walk_data(self, *ent):
        for jsv in ent:
            if isinstance(jsv['data'], list):
                ind = int(jsv['offset']['immediates'])+1
                for i in jsv['data']:
                    self.append(f'mem[{ind}] = {i}') 
                    ind += 1
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
            elif name == 'table':
                print(obj)
            elif name == 'function':
                self.typemap = obj['entries']
            else:
                pass
    def walk_op(self, op):
        self.walks[op['name']](self, op)
    def walk_fn_body(self, locs, code):
        self.ends = ['']
        self.blockc = 0
        self.localc = 0
        self.append(f'function f{self.fnc}(stack)')
        self.tape = []
        self.places = []
        self.enter()
        nargc = self.types[self.typemap[self.typec]]
        for i in range(nargc)[::-1]:
            self.append(f'local l{i} = stack[#stack]')
            self.append('stack[#stack] = nil')
        localc = 0
        for i in locs:
            localc += i['count']
        if localc > 0:
            s = []
            for i in range(localc):
                n = nargc + i
                s.append('l' + str(n))
            ss = ', '.join(s)
            self.append(f'local {ss}')
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
    def tape_append(self, *ops, **kops):
        # if ops[0] == 
        print(*ops)
        if len(kops) > 0:
            print('    ' + str(kops))

    def walk_code(self, *args):
        for i in args:
            self.walk_fn_body(i['locals'], i['code'])
    def get_code(self):
        return '\n'.join(self.code)
cc = Compiler('out.json')
cc.all()
with open('out.lua', 'w') as f:
    with open('def.lua') as d:
        c = d.read()
    f.write(c)
    f.write('\n')
    f.write(cc.get_code())