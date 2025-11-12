#!/usr/bin/env python3
import sys, os
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler
from .vm import VM

def usage():
    print("콜 [소스코드_파일] [--디버그|-디]")

def main():
    argv = sys.argv
    if len(argv) < 2:
        usage()
        return
    
    is_debug: bool = False
    if len(argv) >= 3 and argv[2] in ["--디버그","-디"]:
        is_debug = True
    file_path = argv[1]
    
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"{file_path}에서 코드를 찾을 수 없습니다.")
        return
    
    lexer = Lexer(code)
    if is_debug:
        lexer.print()
        lexer.__init__(code)
    parser = Parser(lexer)
    ast = parser.parse()
    if is_debug:
        print(ast)
    main_compiler = Compiler()
    main_compiler.compile_main(ast)
    vm = VM(main_compiler.assign, main_compiler.const_pool,
            main_compiler.bytecode)
    vm.run()
