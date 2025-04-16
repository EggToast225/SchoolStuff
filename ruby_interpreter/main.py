def run(fn,text):
    from Lexer import Lexer
    from Parser import Parser
    from Interpreter import Interpreter
    from Context import Context
    from GlobalSymbolTable import global_symbol_table
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



