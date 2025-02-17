###############
#   IMPORTS
###############

from strings_with_arrows import * 



#Initialize Types and Characters
# These are End of Files (EOF), ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT

(EOF, ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT, LPARAN, RPARAN) = 'EOF', 'ADD', 'SUBSTRACT', 'MULTIPLY', 'DIVIDE', 'FLOAT', 'INT', 'LPARAN', 'RPARAN'

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
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, "Runtime Error", details)


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
            elif self.current_char.isdigit():
                tokens.append(self.make_numbers())
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

        while self.current_char != None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0: return Token(INT, int(num_str), pos_start, self.pos)
        elif dot_count == 1: return Token(FLOAT, float(num_str), pos_start, self.pos)    




### Grammer
'''
expr    : term ((PLUS|MINUS) term)*

term    : factor ((MUL|DIV) factor)*

factor  : INT:FLOAT
        : (PLUS|MINUS) factor
        : LPARAN expr RPARAN


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
                "Expected '+', '-' , '*' , or '/'"
                ))
        return res
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (ADD, SUBTRACT): # Unary 
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.type in (INT, FLOAT):    # Integers
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == LPARAN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == RPARAN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end, 
            "Expected int or float"
            ))
    
        

    def term(self): # Cals self.factor and has MULTIPLY and DIVIDE operators
        return self.binary_operation(self.factor, (MULTIPLY, DIVIDE))

    def expr(self): # calls self.term and has ADD, SUB operators
        return self.binary_operation(self.term, (ADD, SUBTRACT))


        # This basically takes a function, makes it run it's generic code with it's operator rules
    def binary_operation(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: 
            return res


        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
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
    

    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None
        
    def multiply_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None
        
    def divide_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.pos_start, other.pos_end, "Divison by zero")
            return Number(self.value / other.value), None
    
    def __repr__(self):
        return str(self.value)
        
#################
#   Interpreter
###################

class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}' # method name is set as the type of name]
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self,node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self,node):
        return RTEResult().success(
            Number(node.tok.value).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperatorNode(self,node):
        # after finding binary operator, needs to find left number node and right number node
        res = RTEResult()

        left = res.register(self.visit(node.left_node)) # get left node
        if res.error:
            return res
        
        right = res.register(self.visit(node.right_node)) # get right node
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
        

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))


    def visit_UnaryOpNode(self,node):
        res = RTEResult()
        number = res.register(self.visit(node.node))
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
    result = interpreter.visit(ast.node)
    

    return result.value, result.error