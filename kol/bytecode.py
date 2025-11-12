from .vm import VM
from .frame import Frame
from .func import Func
from .ast import FuncAST
from .struct import Class, Struct
import types
function = types.FunctionType


class Bytecode:
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        raise Exception("에러")
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
class StoreFromConstPool(Bytecode):
    def __init__(self, const_index, scope_index):
        self.const_index = const_index
        self.scope_index = scope_index

    def __call__(self, vm: VM):
        if vm.frames:
            vm.frames[-1].local_list[self.scope_index] = \
                vm.const_pool[self.const_index]
        else:
            vm.global_list[self.scope_index] = vm.const_pool[self.const_index]

    def __repr__(self):
        return f"LoadConstPool(const_index={self.const_index!r})"

class LoadConst(Bytecode):
    def __init__(self, const):
        self.const = const

    def __call__(self, vm: VM):
        vm.stack.append(self.const)

    def __repr__(self):
        return f"LoadConst(const={self.const!r})"


class LoadGlobal(Bytecode):
    def __init__(self, index):
        self.index = index

    def __call__(self, vm: VM):
        vm.stack.append(vm.global_list[self.index])

    def __repr__(self):
        return f"LoadGlobal(index={self.index!r})"

class LoadLocal(Bytecode):
    def __init__(self, index):
        self.index = index

    def __call__(self, vm: VM):
        vm.stack.append(vm.frames[-1].local_list[self.index])

    def __repr__(self):
        return f"LoadLocal(index={self.index!r})"

class StoreGlobal(Bytecode):
    def __init__(self, index):
        self.index = index

    def __call__(self, vm: VM):
        top = vm.stack.pop()
        if isinstance(top, (Struct, Class)):
            top = top.copy()
        vm.global_list[self.index] = top

    def __repr__(self):
        return f"StoreGlobal(index={self.index!r})"

class StoreLocal(Bytecode):
    def __init__(self, index):
        self.index = index

    def __call__(self, vm: VM):
        top = vm.stack.pop()
        if isinstance(top, (Struct, Class)):
            top = top.copy()
        vm.frames[-1].local_list[self.index] = top

    def __repr__(self):
        return f"StoreLocal(index={self.index!r})"

class StoreField(Bytecode):
    def __init__(self, field:str):
        self.field = field

    def __call__(self, vm: VM):
        obj = vm.stack.pop()
        rvalue = vm.stack.pop()
        obj[self.field] = rvalue

    def __repr__(self):
        return f"StoreField(field={self.field!r})"

class StoreIndex(Bytecode):
    def __call__(self, vm: VM):
        top = vm.stack.pop()
        if len(vm.frames[-1].local_list) == self.index:
            vm.frames[-1].local_list.append(top)
        elif len(vm.frames[-1].local_list) > self.index:
            vm.frames[-1].local_list[self.index] = top
        else:
            raise Exception("에러")

class BuildArray(Bytecode):
    def __init__(self, array_len):
        self.array_len = array_len

    def __call__(self, vm: VM):
        if self.array_len == 0:
            vm.stack.append([])
            return
        
        arr = vm.stack[-self.array_len:]
        vm.stack = vm.stack[:-self.array_len]
        vm.stack.append(arr)

    def __repr__(self):
        return f"BuildArray(array_len={self.array_len!r})"

class BuildDict(Bytecode):
    def __init__(self, key_value_len):
        self.key_value_len = key_value_len

    def __call__(self, vm: VM):
        dic = {}
        for _ in range(self.key_value_len):
            value = vm.stack.pop()
            key = vm.stack.pop()
            dic[key] = value
        vm.stack.append(dic)

    def __repr__(self):
        return f"BuildDict(key_value_len={self.key_value_len!r})"
    
class Pop(Bytecode):
    def __call__(self, vm):
        vm.stack.pop()

class JumpCode(Bytecode):
    def __init__(self, ip = None):
        self.ip = ip

    def bind(self, ip):
        self.ip = ip

    def __repr__(self):
        return f"{self.__class__.__name__}(ip={self.ip!r})"
        
class Jmp(JumpCode):

    def __call__(self, vm: VM):
        if vm.frames:
            vm.frames[-1].ip = self.ip - 1
        else:
            vm.ip = self.ip -1
        

class JmpIfTrue(JumpCode):

    def __call__(self, vm: VM):
        if vm.stack.pop():
            if vm.frames:
                vm.frames[-1].ip = self.ip - 1
            else:
                vm.ip = self.ip - 1
        
class JmpIfFalse(JumpCode):

    def __call__(self, vm: VM):
        if not vm.stack.pop():
            if vm.frames:
                vm.frames[-1].ip = self.ip - 1
            else:
                vm.ip = self.ip - 1

class ForInPrepare(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        if vm.frames:
            vm.frames[-1].for_iter.append(iter(vm.stack.pop()))
        else:
            vm.for_iter.append(iter(vm.stack.pop()))

class ForInStep(Bytecode):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return f"ForInStep(index={self.index!r})"

    def __call__(self, vm: VM):
        try:
            if vm.frames:
                obj = next(vm.frames[-1].for_iter[-1])
                vm.frames[-1].local_list[self.index] = obj
            else:
                obj = next(vm.for_iter[-1])
                vm.global_list[self.index] = obj
            vm.stack.append(True)
        except StopIteration:
            vm.stack.append(False)

class ForInDone(Bytecode):
    def __call__(self, vm):
        if vm.frames:
            vm.frames[-1].for_iter.pop()
        else:
            vm.for_iter.pop()

class Call(Bytecode):
    def __init__(self, param_count):
        self.param_count = param_count

    def __call__(self, vm: VM):
        from .compiler import Compiler
        func: Func = vm.stack.pop()
        if self.param_count != len(func.args):
            raise Exception("실행 에러: 호출된 매개변수와 함수의 매개변수가 다름")
        
        if isinstance(func.code, FuncAST):
            Compiler.compile_func(func, vm.const_pool)
        args = vm.stack[-len(func.args):]
        vm.stack = vm.stack[:-len(func.args)]
        
        
        if isinstance(func.code, function):
            ret = func.code(*args)
            vm.stack.append(ret)
        else:
            vm.frames.append(Frame(func, args))

    def __repr__(self):
        return f"Call(param_count={self.param_count!r})"

class Ret(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        vm.frames.pop()
        

        
class LoadField(Bytecode):
    def __init__(self, field):
        self.field = field

    def __call__(self, vm: VM):
        obj = vm.stack.pop()
        vm.stack.append(obj[self.field])

    def __repr__(self):
        return f"LoadField(field={self.field!r})"

class LoadIndex(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        index = vm.stack.pop()
        obj = vm.stack.pop()
        vm.stack.append(obj[index])

class LoadMethod(Bytecode):
    def __init__(self, method):
        self.method = method

    def __call__(self, vm: VM):
        obj:Class = vm.stack.pop()
        vm.stack.append(obj.get_method(self.method))

    def __repr__(self):
        return f"LoadMethod(method={self.method!r})"


class EqualOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()

        vm.stack.append(obj1 == obj2)


class NotEqualOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()

        vm.stack.append(obj1 != obj2)

class LikeOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
            
        if obj1 is None:
            if obj2 is False or obj2 == 0 or obj2 == "":
                vm.stack.append(True)
                return
        if obj2 is None:
            if obj1 is False or obj1 == 0 or obj1 == "":
                vm.stack.append(True)
                return
            
        try:
            if isinstance(obj1, str) and isinstance(obj2, (int, float)):
                vm.stack.append(float(obj1) == obj2)
                return
            if isinstance(obj1, (int, float)) and isinstance(obj2, str):
                vm.stack.append(obj1 == float(obj2))
                return
        except ValueError:
            if isinstance(obj1, str) and isinstance(obj2, (int, float)):
                vm.stack.append(0.0 == obj2)
                return
            if isinstance(obj1, (int, float)) and isinstance(obj2, str):
                vm.stack.append(obj1 == 0.0)
                return

        vm.stack.append(obj1 == obj2)

class NotLikeOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
            
        if obj1 is None:
            if obj2 is False or obj2 == 0 or obj2 == "":
                vm.stack.append(False)
                return
        if obj2 is None:
            if obj1 is False or obj1 == 0 or obj1 == "":
                vm.stack.append(False)
                return
            
        try:
            if isinstance(obj1, str) and isinstance(obj2, (int, float)):
                vm.stack.append(float(obj1) != obj2)
                return
            if isinstance(obj1, (int, float)) and isinstance(obj2, str):
                vm.stack.append(obj1 != float(obj2))
                return
        except ValueError:
            if isinstance(obj1, str) and isinstance(obj2, (int, float)):
                vm.stack.append(0.0 != obj2)
                return
            if isinstance(obj1, (int, float)) and isinstance(obj2, str):
                vm.stack.append(obj1 != 0.0)
                return

        vm.stack.append(obj1 != obj2)
    

class GEOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
        vm.stack.append(obj1 >= obj2)

class GTOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
        vm.stack.append(obj1 > obj2)
class LEOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
        vm.stack.append(obj1 <= obj2)
class LTOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        obj2 = vm.stack.pop()
        obj1 = vm.stack.pop()
        vm.stack.append(obj1 < obj2)

class SHLOp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        count = vm.stack.pop()
        num = vm.stack.pop()
        vm.stack.append(num << count)

class SHROp(Bytecode):
    def __init__(self):
        pass

    def __call__(self, vm: VM):
        count = vm.stack.pop()
        num = vm.stack.pop()
        vm.stack.append(num >> count)