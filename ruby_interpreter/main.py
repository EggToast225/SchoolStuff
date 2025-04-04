from token import NUMBER
from Interpreter import *
from Parser import *
from Lexer import *
from Context import *

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

def run(fn,text):
    lexer  = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error 


    #Generate Abstract Syntax Tree
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Run Program
    interpreter = Interpreter()
    context = Context("<program>", )
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    

    return result.value, result.error

while True:
    text = input('basic > ')
    result, error = run("<stdin>", text)

    if error: print(error.as_string())
    else: print(result)