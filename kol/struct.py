import copy

class Struct:
    def __init__(self, var):
        self.var = {}
        for name in var:
            self.var[name] = None
        self.is_type = True

    def __getitem__(self, name):
        return self.var[name]
    
    def __setitem__(self, name, obj):
        self.var[name] = obj

    def copy(self):
        
        if self.is_type:
            obj = copy.deepcopy(self)
            obj.is_type = False
            return obj
        else:
            return self

class Class(Struct):
    def __init__(self, var:list, funcs, parent):
        if parent:
            var += list(parent.var)
        
        super().__init__(var)
        self.parent = parent
        if hasattr(parent, "funcs"):
            funcs = parent.funcs|funcs
        self.funcs = funcs

    def __getitem__(self, name):
        return self.var[name]
    
    def __setitem__(self, name, obj):
        return super().__setitem__(name, obj)
    
    def get_method(self, name):
        return self.funcs[name]