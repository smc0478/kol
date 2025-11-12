from .frame import Frame
from .builtin import builtins
class VM:
    def __init__(self, global_len, const_pool, bytecode):
        self.stack = []
        self.frames: list[Frame] = []
        self.global_list = [None]*global_len
        self.const_pool = const_pool
        self.global_code = bytecode
        self.for_iter = []
        self.ip = -1
        for i, ident in enumerate(builtins):
            self.global_list[i] = builtins[ident]
        
    def run(self):
        while True:
            if self.frames:
                self.execute_func()
            elif self.execute_main():
                break

    def execute_func(self):
        self.frames[-1].ip += 1
        self.frames[-1].code[self.frames[-1].ip](self)

    def execute_main(self):
        self.ip += 1
        if self.ip >= len(self.global_code):
            return True
        self.global_code[self.ip](self)

        return False
