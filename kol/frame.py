from .func import Func


class Frame:
    def __init__(self, func:Func, params: list):
        self.code = func.code
        self.local_list = [None]*func.local_count
        self.ip = -1
        self.for_iter = []
        for i,param in enumerate(params):
            self.local_list[i] = param