###############
#   IMPORTS
###############

from strings_with_arrows import * 

import string



#Initialize Types and Characters
# These are End of Files (EOF), ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + '0123456789'


###############
#   TOKENS
###############

# Algebraic
(EOF, ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT, LPARAN, RPARAN, POWER) = 'EOF', 'ADD', 'SUBSTRACT', 'MULTIPLY', 'DIVIDE', 'FLOAT', 'INT', 'LPARAN', 'RPARAN', "POWER"

#Variables
(TT_IDENTIFIER, TT_KEYWORD, TT_EQ) ='IDENTIFIER', 'KEYWORD', 'EQ'
'''
    VAR          variable_name       =  <expr>
    ^                ^               ^           
  KEYWORD        IDENTIFIER        EQUALS
'''

KEYWORDS = [
    'VAR'
]

###############
# TOKEN CLASS #
###############

'''
The token class specifies the type and value of the character
class Token(object):
    self.type = type    # token type
    self.value = value  # value of token

    self.pos_start = None   # Entry for Position class optional, if there is, the position class of the Token is copied
    self.pos_end = None     # Entry for Position class optional, if there is, the position class of the Token is copied and advanced
'''

class Token(object):
    def __init__(self, type, value=None, pos_start = None, pos_end = None):
        self.type = type
        self.value = value

        if pos_start: # If there's start position, assign the start as the current position and the end the advance() of the current position
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end: # If there's a end position provided, make start and end the given end position
            self.pos_end = pos_end.copy() 
            self.pos_start = pos_end.copy()

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


############
# ERRORS
############

# The error class shows the position and type of error

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        return result


# Error Types


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)

class RunTimeError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Runtime Error", details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'File {self.pos_start.file_name}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        
        return result

    def generate_traceback(self):
        result =''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' File {pos.file_name}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        
        return "Traceback (most recent call last):\n" + result


######################
# RUNTIME RESULT
######################

class RTEResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: 
            self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
######################
#  CONTEXT
#########################

class Context: # holds current context to hold functions 
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos


########################
# POSITION
########################

class Position:
    def __init__(self, idx, ln, col, file_name, file_txt): # this is the index, line, column, file name and file text
        self.idx = idx
        self.ln = ln
        self.col = col
        self.file_name  = file_name
        self.file_txt = file_txt
    
    def advance(self, current_char = None): # keeps track of index and column
        self.idx += 1
        self.col += 1

        if current_char == '\n': # reset the column and increase line count if there's a newline
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.file_name, self.file_txt)
    


#############
#   LEXER   # 
#############

# The lexer just goes through the string and creates tokens 

class Lexer(object):
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text 
        self.pos = Position(-1,0,-1, fn, text) # position is set to index -1, line 0, column -1
        self.current_char = self.text[self.pos.idx]
        self.advance() # this makes self.pos = 0 when it's initialized


    
    def advance(self):  # increment pos and reassigns current char  if the position index is less than length of text
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None


    # Returns a list of tokens depending on current char in text
    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t': # If the current character is a space or tab, just skip it
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_char in LETTERS:
                tokens.append(self.make_id())
                self.advance()
            elif self.current_char == '+':
                tokens.append(Token(ADD, pos_start = self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(SUBTRACT, pos_start = self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(DIVIDE, pos_start = self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(MULTIPLY, pos_start = self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(LPARAN, pos_start = self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RPARAN, pos_start = self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(POWER, pos_start = self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TT_EQ, pos_start = self.pos))
                self.advance()


            # case of an unrecognized character
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'" ) # returns an empty list and error
            
        tokens.append(Token(EOF, pos_start=self.pos))
        return tokens, None # return tokens and no Errors
    
    # Determines if the number_str is a float or Integer by the number of dots. 
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and (self.current_char in DIGITS or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0: return Token(INT, int(num_str), pos_start, self.pos)
        elif dot_count == 1: return Token(FLOAT, float(num_str), pos_start, self.pos)    
    
    # Makes identifier
    def make_id(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_chat != None and (self.current_char in LETTERS_DIGITS + '_'):
            id_str += self.current_char
            self.advance()
        
        if id_str in KEYWORDS:
            tok_type = TT_KEYWORD
        else:
            tok_type == TT_IDENTIFIER
        
        return Token(tok_type, id_str, pos_start, self.pos)

### Grammer
'''

expr    : KEYWORD:VAR IDENTIFIER EQ expr
        : term ((PLUS|MINUS) term)*

term    : factor ((MUL|DIV) factor)*

factor  : (PLUS|MINUS) factor
        : power

power   : atom (POWER factor)*

atom    : INT | FLOAT
        : LPAREN expr RPAREN


'''

##################
# NODES
#################

class NumberNode:
    def __init__(self,tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class BinaryOperatorNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


# VARIABLES
class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
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
        self.error = None
        self.node = None
    
    def register(self, res):
        if isinstance(res, ParseResult): #Tracks errors if there is an error
            if res.error: 
                self.error = res.error
            return res.node
    
        return res

    def success(self, node):
        self.node = node
        return self
    
    def failure(self,error):
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

    def parse(self):
        res = self.expr()
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
                return res.faileure(InvalidSyntaxError(
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
    
#######################
#   VALUES
####################

class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self,context =None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multiply_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divide_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.pos_start, 
                other.pos_end, "Divison by zero",
                self.context)
            return Number(self.value / other.value).set_context(self.context), None

    def power_by(self,other):
        if isinstance(other,Number):
            return Number(self.value ** other.value).set_context(self.context), None
    
    def __repr__(self):
        return str(self.value)
        
#################
#   Interpreter
###################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}' # method name is set as the type of name]
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self,node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self,node, context):
        return RTEResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperatorNode(self,node, context):
        # after finding binary operator, needs to find left number node and right number node
        res = RTEResult()

        left = res.register(self.visit(node.left_node, context)) # get left node
        if res.error:
            return res
        
        right = res.register(self.visit(node.right_node, context)) # get right node
        if res.error:
            return res
        
        #Check binary node

        if node.op_tok.type == ADD:
            result, error = left.added_to(right)

        elif node.op_tok.type == SUBTRACT:
            result, error = left.subbed_by(right)

        elif node.op_tok.type == MULTIPLY:
            result, error = left.multiply_by(right)

        elif node.op_tok.type == DIVIDE:
            result, error = left.divide_by(right)
        
        elif node.op_tok.type == POWER:
            result, error = left.power_by(right)
        

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))


    def visit_UnaryOpNode(self,node, context):
        res = RTEResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == SUBTRACT:
            number, error = number.multiply_by(Number(-1))
        
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
        

##########
# RUN
##########

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
    result = interpreter.visit(ast.node, context)
    

    return result.value, result.error