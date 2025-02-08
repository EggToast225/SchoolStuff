# Rewritten Interpreter

#Initialize Types and Characters
# These are End of Files (EOF), ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT

(EOF, ADD, SUBTRACT, MULTIPLY, DIVIDE, FLOAT, INT, LPARAN, RPARAN) = 'EOF', 'ADD', 'SUBSTRACT', 'MULTIPLY', 'DIVIDE', 'FLOAT', 'INT', 'LPARAN', 'RPARAN'

###############
# TOKEN CLASS #
###############

# The token class specifies the type and value of the character

class Token(object):
    def __init__(self, type, value = None):
        self.type = type
        self.value = value
    
    def __str__(self):
        return "Token({value}, {type})".format(
            value = self.value,
            type = repr(self.type)
        )
    
    def __repr__(self):
        return self.__str__()


############
# Errors
############

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pod_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'{self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__("Illegal Character", details)

########################
# POSITION
########################

class Position:
    def __innit__(self, idx, ln, col, file_name, file_txt): # this is the index, line, column, file name and file text
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
        self.pos = Position(-1,0,-1) # position is set to index -1, line 0, column -1
        self.current_char = self.text[self.pos]
        self.advance() # this makes self.pos = 0 when it's initialized


    
    def advance(self):  # increment pos and reassigns current char  if the position index is less than length of text
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t': # If the current character is a space or tab, just skip it
                self.advance()
            elif self.current_char.isdigit():
                tokens.append(self.make_numbers())
            elif self.current_char == '+':
                tokens.append(Token(ADD))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(SUBTRACT))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(DIVIDE))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(MULTIPLY))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(LPARAN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RPARAN))
                self.advance()

            # case of an unrecognized character
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'" ) # returns an empty list and error

        return tokens, None # return tokens and no Errors
    

    def make_numbers(self):
        num_str = ''
        dot_count = 0

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0: return Token(int(num_str), INT)
        elif dot_count == 1: return Token(float(num_str),FLOAT)    



##########
# RUN
##########

def run(fn,text):
    lexer  = Lexer(fn,text)
    tokens, error = lexer.make_tokens()

    return tokens, error

