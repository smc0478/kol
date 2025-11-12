from .func import Func

def build_func_object(pyfunc, params_count):
    return Func(pyfunc, params_count=params_count)

def builtin_add(a,b):
    return a+b

def builtin_sub(a,b):
    return a - b

def builtin_mul(a,b):
    return a * b

def builtin_div(a,b):
    if isinstance(a,int) and isinstance(b,int):
        return a//b
    return a / b

def builtin_mod(a,b):
    return a % b

def builtin_read():
    return input()
    
def builtin_println(str):
    return print(builtin_to_string(str))

def builtin_print(str):
    return print(builtin_to_string(str), end="")

def builtin_to_string(obj):
    return str(obj)

def builtin_to_int(obj):
    return int(obj)


def builtin_to_hex(obj):
    return hex(obj)

def builtin_to_float(obj):
    return float(obj)

def builtin_to_bool(obj):
    return bool(obj)

def builtin_length(obj):
    return len(obj)

def builtin_error(str):
    raise Exception(str)

def builtin_range(start, end):
    return list(range(start, end))


def builtin_chr(num):
    return chr(num)

def builtin_ord(s):
    return ord(s)

def builtin_slice(obj, start, end):
    return obj[start:end]

def builtin_in(obj2, obj):
    return obj2 in obj

def builtin_not(a):
    return not a


def builtin_bitnot(a):
    return ~a


def builtin_bitand(a, b):
    return a & b

def builtin_bitor(a, b):
    return a | b

def builtin_bitxor(a, b):
    return a ^ b


def builtin_append(arr: list, obj):
    return arr.append(obj)

def builtin_pop(arr: list):
    return arr.pop()

def builtin_keys(d: dict):
    return d.keys()

def builtin_values(d: dict):
    return d.values()

def builtin_split(s: str, sep):
    return s.split(sep)

def builtin_join(sep: str, arr:list):
    return sep.join(arr)

def builtin_exit(code):
    exit(code)

builtins = {
    "더":build_func_object(builtin_add, 2),
    "뺀":build_func_object(builtin_sub, 2),
    "곱":build_func_object(builtin_mul, 2),
    "나눈":build_func_object(builtin_div, 2),
    "나머지를_구":build_func_object(builtin_mod, 2),
    "입력": build_func_object(builtin_read,0),
    "출력": build_func_object(builtin_println, 1),
    "줄바꿈없이_출력": build_func_object(builtin_print, 1),
    "문자열으로_변환": build_func_object(builtin_to_string, 1),
    "정수로_변환": build_func_object(builtin_to_int, 1),
    "정수_16진수로_변환": build_func_object(builtin_to_hex, 1),
    "소수로_변환": build_func_object(builtin_to_float, 1),
    "진리값으로_변환": build_func_object(builtin_to_bool, 1),
    "길이를_구": build_func_object(builtin_length, 1),
    "범위를_만든": build_func_object(builtin_range, 2),
    "문자로_만든": build_func_object(builtin_chr, 1),
    "정수로_만든": build_func_object(builtin_ord, 1),
    "자른": build_func_object(builtin_slice, 3),
    "에_포함된": build_func_object(builtin_in, 2),
    "부정": build_func_object(builtin_not, 1),
    "반전": build_func_object(builtin_bitnot, 1),
    "논리곱": build_func_object(builtin_bitand, 2),
    "논리합": build_func_object(builtin_bitor, 2),
    "베타적_논리합": build_func_object(builtin_bitxor, 2),
    "추가": build_func_object(builtin_append, 2),
    "하나_꺼낸": build_func_object(builtin_pop, 1),
    "키들을_가져온": build_func_object(builtin_keys, 1),
    "값들을_가져온": build_func_object(builtin_values, 1),
    "쪼갠": build_func_object(builtin_split, 2),
    "합친": build_func_object(builtin_join, 2),
    "종료": build_func_object(builtin_exit, 1),
    "문제가_발생": build_func_object(builtin_error, 1)
}