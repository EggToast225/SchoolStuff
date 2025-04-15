from token import NUMBER
from Interpreter import *
from Parser import *
from Lexer import *
from Context import *
from GlobalSymbolTable import global_symbol_table

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
    if text.strip() == "": continue
    result, error = run("<stdin>", text)

    if error:
        print(error.as_string())
    elif result: 
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))