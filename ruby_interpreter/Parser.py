from Errors import InvalidSyntaxError
from Token import *
from Nodes import *
from ParseResult import ParseResult

###########################################################
'''
    Grammar
    expr
            : KEYWORD:VAR IDENTIFIER EQ expr
            : comp-expr((KEYWORDS:AND | KEYWORD: OR); comp-expr)*
            
            : NOT comp-expr
comp-expr   : arith-expr ((EE|LT|GE|LTE|GTE)) arith-expr)*

arith-expr  : term((PLUS|MINUS) term)*

    term    : factor ((MUL|DIV) factor)*

    factor  : (PLUS|MINUS) factor
            : power

    power   : atom (POWER factor)*

    call    : atom (LPAREN (expr (COMMA IDENTIFIER)*) RPAREN)?

    atom    : INT | FLOAT | STRING | IDENTIFIER
            : LPAREN expr RPAREN
            : list_expr
            : if-expr
            : for-expr
            : while-expr
            : func-def

    if-expr : KEYWORD: IF expr KEYWORD:THEN expr
              (KEYWORD:ELIF expr KEYWORD: THEN expr)*
              (KEYWORD:ELSE expr)?

    for-expr: KEYWORD:FOR IDENTIFIER EQ expr KEYWORD: TO expr
              (KEYWORD:STEP expr)? KEYWORD:THEN expr
    
    while-expr: KEYWORD:WHILE expr KEYWORD:THEN expr

    func-def  : KEYWORD:FUN IDENTIFIER ?
                LPAREN(IDENTIFIER (COMMA IDENTIFIER) *)? RPAREN
                ARROW expr
'''
###########################################################

###############
#   PARSER
###############
# Takes in a list of tokens and evaluates grammer
    
class Parser:
    def __init__(self, tokens): # takes in a list of tokens
        self.tokens = tokens
        self.tok_idx = -1
        self.advance() # when intialized, tok_idx = 0;
    
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def reverse(self):
        self.tok_idx -=1
        if  -1 < self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def parse_next(self, ParseResult):
        ParseResult.register_advancement()
        self.advance()


    def parse(self):
        res = self.expr() # Enters AST tree, with expression being the highest order
        if not res.is_valid() and self.current_tok.type != TT_EOF: # If current_tok type isn't EOF, that means there's been a syntax error
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-' , '*' , '^', or '/'"
                ))
        return res
    
    def call(self):
        res = ParseResult()
        # Search for an atom
        atom = res.register(self.atom())
        res.is_valid()
        
        # If we have ( or list of arguments
        if self.current_tok.type == TT_LPAREN:
            self.parse_next(res)

            arg_nodes = []
            # In the case that we have an parenthesis with no args such as ()
            if self.current_tok.type == TT_RPAREN:
                self.parse_next(res)
            else: # If there are arguments
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')', 'VAR', 'IF', 'FOR','WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[', or 'NOT')"
                ))
                # Argument in comma seperate; get all args and add them to list of args
                while self.current_tok.type == TT_COMMA:
                    self.parse_next(res)
                    arg_nodes.append(res.register(self.expr()))
                    res.is_valid()
                # At the end of the list, close off with a ')'
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')'"
                    ))
                self.parse_next(res)
            # Return the call node
            return res.success(CallNode(atom, arg_nodes))
        # Return a regular atom
        return res.success(atom)



    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_INT, TT_FLOAT):    # Integers
            self.parse_next(res)
            return res.success(NumberNode(tok))
        
        if tok.type == TT_STRING:
            self.parse_next(res)
            return res.success(StringNode(tok))
        
        elif tok.type == TT_IDENTIFIER:
            self.parse_next(res)
            return res.success(VarAccessNode(tok))

        # Parenthesis case handling
        elif tok.type == TT_LPAREN: # Left parenthesis
            self.parse_next(res)
            expr = res.register(self.expr())
            res.is_valid()

            if self.current_tok.type == TT_RPAREN: # Right parenthesis
                self.parse_next(res)
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            res.is_valid()
            return res.success(list_expr)
        
        elif tok.matches(TT_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            res.is_valid()
            return res.success(if_expr)
        
        elif tok.matches(TT_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            res.is_valid()
            return res.success(for_expr)
        
        elif tok.matches(TT_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            res.is_valid()
            return res.success(while_expr)
        
        elif tok.matches(TT_KEYWORD, 'FUN'):
            func_def = res.register(self.func_def())
            res.is_valid()
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int or float, '+', identifier,  '-', or '(', ')', '[', 'VAR', 'IF', 'FOR','WHILE', 'FUN'"
            ))
    
    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))
        self.parse_next(res)

        if self.current_tok.type == TT_RSQUARE:
            self.parse_next(res)
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')', 'VAR', 'IF', 'FOR','WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[', or 'NOT')"
                ))
            # Elements in comma seperate; get all elements

            while self.current_tok.type == TT_COMMA:
                self.parse_next(res)
                element_nodes.append(res.register(self.expr()))
                res.is_valid()

            # At the end of the list, close off with a ']'
            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',', ']'"
                    ))
            self.parse_next(res)
            
        return res.success(ListNode(element_nodes,
                        pos_start,
                        self.current_tok.pos_end.copy()))

        

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        # Checks if IF keyword is used
        if not self.current_tok.matches(TT_KEYWORD, 'IF'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'IF'"
            ))
        # If IF keyword is there, advance to the next part, which is conditions
        self.parse_next(res)

        # Conditional expression
        condition = res.register(self.expr())
        res.is_valid()

        #THEN Keyword check (if the condition is true, then)
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"))
        
        self.parse_next(res)

        expr = res.register(self.expr())
        res.is_valid()

        # Append the cases of the condition
        cases.append((condition, expr))

        # Any number of ELIF statements, similar to IF, but using ELIF
        while self.current_tok.matches(TT_KEYWORD, 'ELIF'):
            self.parse_next(res)

            condition = res.register(self.expr())
            res.is_valid()

            if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'THEN"))
            
            self.parse_next(res)

            expr = res.register(self.expr())
            res.is_valid()

        # ELSE Keyword
        if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
            self.parse_next(res)

            expr = res.register(self.expr())
            res.is_valid()
            else_case = expr

        return res.success(IfNode(cases,else_case))
    
    def for_expr(self):
        res = ParseResult()
        
        # Check if we have FOR
        if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FOR'"
            ))
        
        # If FOR keyword is there, advance to the next part, which is Identifier
        self.parse_next(res)

        # Expect Identifier after FOR
        if self.current_tok.type != TT_IDENTIFIER: 
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))
        
        # Get variable name
        var_name = self.current_tok

        self.parse_next(res)

        # Check for =
        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
        self.parse_next(res)

        start_value = res.register(self.expr())
        res.is_valid()

        if not self.current_tok.matches(TT_KEYWORD, "TO"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'TO'"
            ))
        
        self.parse_next(res)

        end_value = res.register(self.expr())
        res.is_valid()

        if self.current_tok.matches(TT_KEYWORD, 'STEP'):
            self.parse_next(res)
            
            step_value = res.register(self.expr())
            res.is_valid()
        else:
            step_value = None
        
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        self.parse_next(res)

        body = res.register(self.expr())
        res.is_valid()

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'WHILE'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'WHILE'"
                ))
        self.parse_next(res)

        condition = res.register(self.expr())
        res.is_valid()
        
        if self.current_tok.matches(TT_KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'THEN'"
                ))
        
        self.parse_next(res)

        body = res.register(self.expr())
        res.is_valid()

        return res.success(WhileNode(condition, body))


    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_ADD, TT_SUBTRACT): # Unary 
            self.parse_next(res)
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def term(self): # Calls self.factor and has MULTIPLY and DIVIDE operators
        return self.binary_operation(self.factor, (TT_MULTIPLY, TT_DIVIDE))
    
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            self.parse_next(res)

            node = res.register(self.comp_expr())
            res.is_valid()
            return res.success(UnaryOpNode(op_tok, node))

            
        node = res.register(self.binary_operation(
            self.arith_expr, (
                TT_GREATER_THAN,
                TT_LESS_THAN,
                TT_EQUALS_TO,
                TT_GREATER_THAN_EQUALS,
                TT_LESS_THAN_EQUALS,
                TT_NE)))
        
        if res.error: return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected int or float, '+', identifier,  '-', '(', '[', or NOT "
            ))
        return res.success(node)
    
    def arith_expr(self):
        return self.binary_operation(self.term, (TT_ADD, TT_SUBTRACT))
        

    def expr(self): # calls self.term and has ADD, SUB operators; also has variables identifier
        res = ParseResult()
        
        if self.current_tok.matches(TT_KEYWORD, 'VAR'): # If VAR is declared
            self.parse_next(res)
            if self.current_tok.type != TT_IDENTIFIER: # Expect Identifier after VAR
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))
        
        # Handling Variable Access or Assignment
        if self.current_tok.type == TT_IDENTIFIER:
            var_name = self.current_tok 
            self.parse_next(res)
            
            #Check to see if there's an assignment
            if self.current_tok.type == TT_EQ: # In the instance of this being an assignment of a variable
                self.parse_next(res)
                expr = res.register(self.expr()) # Get the expression of that variable

                res.is_valid()
                return res.success(VarAssignNode(var_name, expr)) # Return Assign node
            
            self.reverse() # In the case that it's not an assignment, we need to go backtrack

        node = res.register(self.binary_operation(self.comp_expr, ((TT_KEYWORD, "AND"), (TT_KEYWORD, "OR"))))
        
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', or '(', '[', 'IF', 'FOR','WHILE', and 'FUN'"
            ))
        return res.success(node)


    def power(self):
        return self.binary_operation(self.call, (TT_POWER, ), self.factor)


        # This basically takes a function, makes it run it's generic code with it's operator rules
    def binary_operation(self, func, ops, func_b =None):
        if func_b == None:
            func_b = func

        res = ParseResult()
        left = res.register(func()) # Get left-side expression
        res.is_valid()

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok # Get operator token
            self.parse_next(res)
            right = res.register(func_b()) # Get right-side expression
            res.is_valid()
            left = BinaryOperatorNode(left, op_tok, right)
        
        return res.success(left)
    
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'FUN'):
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Function"
                ))
        
        self.parse_next(res)

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            self.parse_next(res)
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '(' or Identifier "
                ))
        self.parse_next(res)

        arg_name_toks = []
        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            self.parse_next(res)

            while self.current_tok.type == TT_COMMA: # Get the list of arguments seperated by commas in a function
                self.parse_next(res)
                
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))

                arg_name_toks.append(self.current_tok)
                self.parse_next(res)

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ')'"
                ))
            else: # In the case that we dont have an identifier for the start
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier or ')'"
                    ))
                
            self.parse_next(res)

            if self.current_tok.type != TT_ARROW:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '->'"
                ))
            
            self.parse_next(res)

            node_to_return = res.register(self.expr())
            res.is_valid()

            return res.success(FunctionDefinitionNode(
                var_name_tok,
                arg_name_toks,
                node_to_return
            ))