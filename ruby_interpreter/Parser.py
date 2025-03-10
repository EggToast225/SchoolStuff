from Errors import InvalidSyntaxError
from Token import *



##################
# NODES
#################
class Node(): pass

# Node for number tokens
# Just turns a number token into a Node
class NumberNode(Node):
    def __init__(self,tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

# Node for Binary Operator Tokens like +, -, *, /, ^
# Requires a left node, operator token, and right node
class BinaryOperatorNode(Node):
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

# Node for Unary Operators like -
# Requires unary token and Node (Usually number Node)
class UnaryOpNode(Node):
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


# VARIABLES
class VarAccessNode(Node):
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode(Node):
    def __init__(self,var_name_tok, value_node):
        self.var_name = var_name_tok
        self.expr = value_node
    
        self.pos_start = self.var_name.pos_start
        self.pos_end = value_node.pos_end
    
    def __repr__(self):
        return f'{self.var_name} = {self.expr}'


########################################
# PARSE RESULT
###################################

class ParseResult: # Class keeps track of Parse results and Nodes
    def __init__(self):
        self.node = None # Stores the Parsed Node
        self.error = None # Stores Errors
        
    
    #Tracks errors if there is an error
    def register(self, res):
        if isinstance(res, ParseResult): # If 'res' is a ParseResult Object
            if res.error: # If there is an error in result
                self.error = res.error # Store the error in 'self.error'
            return res.node # Return the actual parsed node
    
        return res  # If res is not a ParsedResult, return it directly

    def success(self, node): # Stores the parsed node provided
        self.node = node
        return self
    
    def failure(self,error): # Used when an unexpected Error occurs; error will store IllegalCharError object
        self.error = error
        return self


    

########################################
# PARSER
###################################

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
    
    ###########################################################
    '''
    Grammer
    expr    : KEYWORD:VAR IDENTIFIER EQ expr
            : term ((PLUS|MINUS) term)*

    term    : factor ((MUL|DIV) factor)*

    factor  : (PLUS|MINUS) factor
            : power

    power   : atom (POWER factor)*

    atom    : INT | FLOAT
            : LPAREN expr RPAREN
    '''
    ###########################################################

    def parse(self):
        res = self.expr() # Enters AST tree, with expression being the highest order
        if not res.error and self.current_tok.type != EOF: # If current_tok type isn't EOF, that means there's been a syntax error
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-' , '*' , '^', or '/'"
                ))
        return res
    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (INT, FLOAT):    # Integers
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            res.success(VarAccessNode(tok))

        # Parenthesis case handling
        elif tok.type == LPARAN: # Left parenthesis
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res

            if self.current_tok.type == RPARAN: # Right parenthesis
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
            
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end, 
            "Expected int or float, '+',  '-', or '(' )"
            ))
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (ADD, SUBTRACT): # Unary 
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def term(self): # Calls self.factor and has MULTIPLY and DIVIDE operators
        return self.binary_operation(self.factor, (MULTIPLY, DIVIDE))

    def expr(self): # calls self.term and has ADD, SUB operators; also has variables identifier
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type == KEYWORDS and tok.value == 'VAR': # Check to see if the token type is a keyword and is a variable
            res.register(self.advance())
            
            if tok.type != TT_IDENTIFIER: # in the case that the next token is not an identifier, return an error
                return res.failure (InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected Identifier"
                ))
            # if it checks out, the variable_name is the token
            var_name = tok
            # we advance to the next position of tokens, which should be a TT_EQ
            res.register(self.advance())

            if tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected Assignment"
                ))
            res.register(self.advance())

            # After this, we look for an expression
            expr = res.register(self.expr())
            if res.error(): return res
            return res.success(VarAssignNode(var_name, expr))

        return self.binary_operation(self.term, (ADD, SUBTRACT))

    def power(self):
        return self.binary_operation(self.atom, (POWER, ), self.factor)


        # This basically takes a function, makes it run it's generic code with it's operator rules
    def binary_operation(self, func, ops, func_b =None):
        if func_b == None:
            func_b = func

        res = ParseResult()
        left = res.register(func())
        if res.error: 
            return res


        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func_b())
            if res.error:
                return res
            left = BinaryOperatorNode(left, op_tok, right)
        
        return res.success(left)
    