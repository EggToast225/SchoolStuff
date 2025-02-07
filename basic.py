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
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result

class IllegalCharError(Error):
    def __init__(self,details):
        super().__init__("Illegal Character", details)


#############
#   LEXER   # 
#############

# The lexer just goes through the string

class Lexer(object):
    def __init__(self,  text):
        self.text = text 
        self.pos = -1
        self.current_char = self.text[self.pos]
        self.advance()

    
    def advance(self):  # increment pos and reassigns current char
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None



    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t': # If the current character is a space or tab, just skip it
                self.advance()
            elif self.current_char.isdigit():
                tokens.append(self.make_numbers())
            elif self.current_char == '+':
                tokens.append(Token(ADD))
            elif self.current_char == '-':
                tokens.append(Token(SUBTRACT))
            elif self.current_char == '/':
                tokens.append(Token(DIVIDE))
            elif self.current_char == '*':
                tokens.append(Token(MULTIPLY))
            elif self.current_char == '(':
                tokens.append(Token(LPARAN))
            elif self.current_char == ')':
                tokens.append(Token(RPARAN))
            else:
                char = self.current_char
                self.advance()
                return [], IllegalCharError("'" + char + "'" )

        return tokens, None
    

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



########
# RUN
######

def run(text):
    lexer  = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error