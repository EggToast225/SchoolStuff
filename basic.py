###############
#   IMPORTS
###############

from strings_with_arrows import * 


# Rewritten Interpreter



#Initialize Types and Characters
# These are End of Files (EOF), ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT

(EOF, ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT, LPARAN, RPARAN) = 'EOF', 'ADD', 'SUBSTRACT', 'MULTIPLY', 'DIVIDE', 'FLOAT', 'INT', 'LPARAN', 'RPARAN'

###############
# TOKEN CLASS #
###############

# The token class specifies the type and value of the character

class Token(object):
    def __init__(self, type, value=None, pos_start = None, pos_end = None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
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
        self.pod_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details} '
        result += f'File {self.pos_start.file_name}, line {self.pos_start.ln}'
        result += '\n\n' + string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)


########################
# POSITION
########################

class Position:
    def __init__(self, idx, ln, col, file_name, file_txt): # this is the index, line, column, file name and file text
        self.idx = idx
        self.ln = ln
        self.col = col
        self.file_name  = file_name
        self.file_text = file_txt
    
    def advance(self, current_char): # keeps track of index and column
        self.idx += 1
        self.col += 1

        if current_char == '\n': # reset the column and increase line count if there's a newline
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.file_name, self.file_text)
    


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


    # Returns a list of tokens
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
            
        tokens.append(Token(EOF), pos_start=self.pos)
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

'''

##################
# NODES
#################

class NumberNode:
    def __init__(self,tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class BinaryOperatorNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    

########################################
# PARSE RESULT
###################################

class ParseResult: # Class keeps track of Parse results and Nodes
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self, res):
        if isinstance(res, ParseResult): #Tracks errors if there is an error
            if res.error: self.error = res.error
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
    
class Parser:
    def __init__(self, tokens): # takes in a list of tokens
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    ###########################################################

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.start_pos, self.current_tok.pos_end, 
                "Expected '+', '-' , '*' , or '/'"
                ))
        return res
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (INT, FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.post_end, "Expected int or float"))
    
        

    def term(self): # Cals self.factor and has MULTIPLY and DIVIDE operators
        return self.binary_operation(self.factor, (MULTIPLY, DIVIDE))

    def expr(self): # calls self.term and has ADD, SUB operators
        return self.binary_operation(self.term, (ADD, SUBTRACT))


        # This basically takes a function, makes it run it's generic code with it's operator rules
    def binary_operation(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res


        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinaryOperatorNode(left, op_tok, right)
        
        return res.success(left)


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

    return ast, None
