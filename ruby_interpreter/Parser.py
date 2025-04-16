from Errors import InvalidSyntaxError
from Token import *
from Nodes import *
from ParseResult import ParseResult

###########################################################
'''
    Grammar

statements      : NEWLINES* statement(NEWLINE+ statement)* NEWLINE

statement       : KEYWORD:RETURN expr?
                : KEYWORD:CONTINUE
                : KEYWORD:BREAK
                : expr

    expr
                : KEYWORD:VAR IDENTIFIER EQ expr
                : comp-expr((KEYWORDS:AND | KEYWORD: OR); comp-expr)*
            
                : NOT comp-expr
comp-expr       : arith-expr ((EE|LT|GE|LTE|GTE)) arith-expr)*

arith-expr      : term((PLUS|MINUS) term)*

    term        : factor ((MUL|DIV) factor)*

    factor      : (PLUS|MINUS) factor
                : power

    power       : atom (POWER factor)*

                    # This is because parentheses are optional in ruby
    call        : atom (LPAREN (expr (COMMA IDENTIFIER)*) RPAREN | (expr (COMMA IDENTIFIER)*) )?

    
    atom        : INT | FLOAT | STRING | IDENTIFIER
                : LPAREN expr RPAREN
                : list_expr
                : if-expr
                : for-expr
                : while-expr
                : func-def

    if-expr     : KEYWORD: IF expr KEYWORD:THEN
                  (expr elif-expr|else-expr?)|(NEWLINE statements KEYWORD:END elif-expr|else-expr)

    elif-expr   : KEYWORD: ELIF expr KEYWORD:THEN
                  (expr elif-expr|else-expr?)|(NEWLINE statements KEYWORD:END elif-expr|else-expr)

    else-expr   : KEYWORD: ELSE
                  expr|(NEWLINE statements KEYWORD:END)
                  

    for-expr    : KEYWORD:FOR IDENTIFIER EQ expr KEYWORD: TO expr
                  (KEYWORD:STEP expr)? KEYWORD:THEN expr
                  expr|(NEWLINE statements KEYWORD:END)
    
    while-expr  : KEYWORD:WHILE expr KEYWORD:THEN expr
                  expr|(NEWLINE statements KEYWORD:END)

    func-def    : KEYWORD:FUN IDENTIFIER ?
                  LPAREN(IDENTIFIER (COMMA IDENTIFIER) *)? RPAREN
                  (ARROW expr)|(NEWLINE statements KEYWORD:END)
'''
###########################################################

###############
#   PARSER
###############
# Takes in a list of tokens and turns it into a AST following a grammer rule with precedences 
    
class Parser:
    def __init__(self, tokens): # takes in a list of tokens
        self.tokens = tokens
        self.tok_idx = -1
        self.advance() # when intialized, tok_idx = 0;
    
    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok
    
    def reverse(self, amount = 1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok
    
    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements() # Enters AST tree, with expression being the highest order

        if not res.error and self.current_tok.type != TT_EOF: # If current_tok type isn't EOF, that means there's been a syntax error
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Token cannot appear after previous tokens"
                ))
        return res
    
##################################################

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE: # Skip the NEWLINE tokens
            res.register_advancement()
            self.advance()
        
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True: # Find more statements which are separated by newlines
            new_line_count = 0 # Step is to get new line, then statement, then repeat until no statements or newline
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                new_line_count += 1
            if new_line_count == 0:
                more_statements = False

            if not more_statements: break # If there are no more statements, get out of loop
            # Otherwise, try to register each statement
            statement = res.try_register(self.statement()) # Try register see if there is a statement or not, if not, it returns None
            if not statement:
                self.reverse(res.to_reverse_count) # reverse the advance methods performed
                more_statements = False
                continue
            statements.append(statement)
        
        # Return a list of statements that will be evaluated by the Interpreter
        return res.success(ListNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))
        
    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        
        # Return a ReturnNode
        if self.current_tok.matches(TT_KEYWORD, 'RETURN'):
            res.register_advancement() # Consume Token
            self.advance()

            expr = res.try_register(self.expr()) # expr is optional, so we use try_register
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
        
        # Return a ContinueNode
        if self.current_tok.matches(TT_KEYWORD, 'CONTINUE'):
            res.register_advancement() # Consume Token
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
        
        #Return a BreakNode
        if self.current_tok.matches(TT_KEYWORD, 'BREAK'):
            res.register_advancement() # Consume Token
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
        
        # If there are no keywords like 'RETURN', 'CONTINUE', or 'BREAK', return a expression

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', int, float, identifier, '+', '-', or '(', '[', 'IF', 'FOR','WHILE', and 'FUN'"
            ))
        return res.success(expr)
    
    def expr(self): # calls self.term and has ADD, SUB operators; also has variables identifier
        res = ParseResult()
        
        if self.current_tok.matches(TT_KEYWORD, 'VAR'): # If VAR is declared
            res.register_advancement() # Consume Token
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER: # Expect Identifier after VAR
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))
        
        # Handling Variable Access or Assignment
        if self.current_tok.type == TT_IDENTIFIER:
            var_name = self.current_tok 
            res.register_advancement()
            self.advance()
            
            #Check to see if there's an assignment
            if self.current_tok.type == TT_EQ: # In the instance of this being an assignment of a variable
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr()) # Get the expression of that variable

                if res.error: return res
                return res.success(VarAssignNode(var_name, expr)) # Return Assign node
            
            self.reverse() # In the case that it's not an assignment, we need to go backtrack

        node = res.register(self.binary_operation(self.comp_expr, ((TT_KEYWORD, "AND"), (TT_KEYWORD, "OR"))))
        
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', or '(', '[', 'IF', 'FOR','WHILE', and 'FUN'"
            ))
        return res.success(node)

    def call(self):
        res = ParseResult()
        # Search for an atom
        atom = res.register(self.atom())
        if res.error: return res

        arg_nodes = []

        # If there are arguments surrounded by parenthesis
        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()

            # In the case that we have an parenthesis with no args such as ()
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()

            else: # If there are arguments
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')', 'VAR', 'IF', 'FOR','WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[', or 'NOT')"
                ))

                # Argument in comma seperate; get all args and add them to list of args
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                # At the end of the list, close off with a ')'
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')'"
                    ))
                res.register_advancement()
                self.advance()
            # Return the call node
            return res.success(CallNode(atom, arg_nodes))
        # if there are no parenthesis

        elif self.current_tok.type in [TT_IDENTIFIER, TT_STRING, TT_INT, TT_FLOAT]:
            argument = res.register(self.expr()) 
            if res.error:
                return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')', 'VAR', 'IF', 'FOR','WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[', or 'NOT')"
                ))
                
            arg_nodes.append(argument) # whatever is after the function name is the expression
            
                # Argument in comma seperate; get all args and add them to list of args
            while self.current_tok.type == TT_COMMA: # this is true for ruby:  puts arg1, arg2
                res.register_advancement()
                self.advance()

                # Add these to arguments to be evaluated
                argument = res.register(self.expr())
                if res.error: return res
                arg_nodes.append(argument)
                
            # Ok now we return this as a regular callnode
            return res.success(CallNode(atom, arg_nodes))
        
        # Return a regular atom
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_INT, TT_FLOAT):    # Integers
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        
        if tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        # Parenthesis case handling
        elif tok.type == TT_LPAREN: # Left parenthesis
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr()) # Expression
            if res.error: return res

            if self.current_tok.type == TT_RPAREN: # Right parenthesis
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)
        
        elif tok.matches(TT_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)
        
        elif tok.matches(TT_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        
        elif tok.matches(TT_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        
        elif tok.matches(TT_KEYWORD, 'FUN'):
            func_def = res.register(self.func_def())
            if res.error: return res
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
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')', 'VAR', 'IF', 'FOR','WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[', or 'NOT')"
                ))
            
            # Elements in comma seperate; get all elements
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

            # At the end of the list, close off with a ']'
            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',', ']'"
                ))
            
            res.register_advancement()
            self.advance()
            
        return res.success(ListNode(
            element_nodes,
            pos_start,
            self.current_tok.pos_end.copy()))
    
    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('IF'))
        if res.error: return res
        cases, else_cases = all_cases
        return res.success(IfNode(cases, else_cases))
    
    def elif_expr(self):
        return self.if_expr_cases('ELIF')
    
    def else_expr(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements()) # get all the statements or lines
                if res.error: return res
                else_case = (statements, True)


                if self.current_tok.matches(TT_KEYWORD, 'END'): # Look to see if there is an END keyword
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected 'END'"
                    ))
        else:
            expr = res.register(self.statement())
            if res.error: return res
            else_case = (expr, False)
        
        return res.success(else_case)


    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        # Checks if IF keyword is used
        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))
        
        # If IF keyword is there, advance to the next part, which is conditions
        res.register_advancement()
        self.advance()

        # Conditional expression
        condition = res.register(self.expr())
        if res.error: return res

        #THEN Keyword check (if the condition is true, then)
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"))
        
        res.register_advancement()
        self.advance()

        # Now check if there are newlines or not
        # If there are multiple lines or newlines, we have to do a different approach to the parser
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements()) # get all the statements or lines
            if res.error: return res
            cases.append((condition, statements, True)) # Include a tuple with condition, statements, and Boolean True

            if self.current_tok.matches(TT_KEYWORD, 'END'): # Look to see if there is an END keyword
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_elif_or_else()) # Look if there are elif or else cases
                if res.error: return res
                new_cases, else_case, = all_cases
                cases.extend(new_cases)
        #If there isn't a newline character
        else:
            # IF condition: THEN expression
            expr = res.register(self.statement())
            if res.error: return res

            # Append the cases of the condition
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_elif_or_else()) # Look if there are elif or else cases
            if res.error: return res
            new_cases, else_case, = all_cases
            cases.extend(new_cases)
        
        return res.success((cases,else_case))
    
    def if_expr_elif_or_else(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'ELIF'):
            all_cases = res.register(self.elif_expr())
            if res.error: return res
            cases, else_case = all_cases # update elif and else cases
        else:
            else_case = res.register(self.else_expr()) # only update the else case
            if res.error: return res

        return res.success((cases, else_case))
    
    def for_expr(self):
        res = ParseResult()
        
        # Check if we have FOR
        if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FOR'"
            ))
        
        # If FOR keyword is there, advance to the next part, which is Identifier
        res.register_advancement()
        self.advance()

        # Expect Identifier after FOR
        if self.current_tok.type != TT_IDENTIFIER: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected Identifier"
            ))
        
        # Get variable name
        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        # Check for '='
        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
        
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, "TO"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'TO'"
            ))
        
        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'STEP'):
            res.register_advancement()
            self.advance()
            
            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None
        
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res
            
            if not self.current_tok.matches(TT_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'END'"
                ))
            
            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'WHILE'"
            ))
        
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res
        
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'THEN'"
            ))
        
        res.register_advancement()
        self.advance()

        # IF NEWLINE
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res
            
            if not self.current_tok.matches(TT_KEYWORD, 'END'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'END'"
                ))
            
            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))


    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_ADD, TT_SUBTRACT): # Unary 
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def term(self): # Calls self.factor and has MULTIPLY and DIVIDE operators
        return self.binary_operation(self.factor, (TT_MULTIPLY, TT_DIVIDE))
    
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
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
        
    def power(self):
        return self.binary_operation(self.call, (TT_POWER, ), self.factor)


        # This basically takes a function, creates a AST Tree
    def binary_operation(self, func, ops, func_b =None):
        if func_b == None:
            func_b = func

        res = ParseResult()
        left = res.register(func()) # Get left-side expression
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok # Get operator token
            
            res.register_advancement()
            self.advance()
            
            right = res.register(func_b()) # Get right-side expression
            if res.error: return res
            left = BinaryOperatorNode(left, op_tok, right)
        
        return res.success(left)
    
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'FUN'):
            return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Function"
                ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
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
            
        res.register_advancement()
        self.advance()

        arg_name_toks = []

        # If there is an identifier for the start
        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA: # Get the list of arguments seperated by commas in a function
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

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

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error: return res

            # In the instance of '->', set auto_return to True
            return res.success(FunctionDefinitionNode(
                var_name_tok,
                arg_name_toks,
                body,
                True
                ))
            
        if self.current_tok.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '->' or NEWLINE"
            ))
        
        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res
    
        if not self.current_tok.matches(TT_KEYWORD, 'END'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'END'"
            ))
        
        res.register_advancement()
        self.advance()

        return res.success(FunctionDefinitionNode(
            var_name_tok,
            arg_name_toks,
            body,
            False
            ))