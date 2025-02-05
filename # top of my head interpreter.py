# top of my head interpreter

# declare types : for this were going to use plus and minus

(EOF, INTEGER, PLUS, MINUS,
LEFT_P, RIGHT_P, DIV, MUL) = (
'EOF', 'INTEGER','PLUS', 'MINUS',
'LEFT_P', 'RIGHT_P', 'DIV', 'MUL')

class Token(object):
    def __init__(self, value, type):
        self.value = value 
        self.type = type

    def __str__(self):
        return 'Token({value}, {type})'.format(value = self.value,
                                               type = repr(self.type))
    
    def __repr__(self):
        return self.__str__()

# alright, now we need to have another class, class of what the functions of an interpreter can do

class Lexer(object):
    def __init__(self,text):
        # start from position 0 from given input
        self.text = text
        self.pos = 0
        self.current_char = text[self.pos]
    
    def error(self):
        raise Exception("Error in parsing")
    
    def advance(self):
        # increments pos value by one and sets current_char variable
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance

    def integer(self): # returns the integer value in the input string, works as a lexemizer
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    def get_next_token(self):   # this is the tokenizer
        # while there is not a next character
        while self.current_char is not None:
            # SKIPS ALL SPACES
            while self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token(self.integer(), INTEGER)
            
            match self.current_char:
                case "+":
                    self.advance() 
                    return Token("+", PLUS)
                case "-":
                    self.advance()
                    return Token("-", MINUS)
                case "/":
                    self.advance()
                    return Token("/", DIV)
                case "*":
                    self.advance()
                    return Token("*", MUL)
                case "(":
                    self.advance()
                    return Token("(", LEFT_P)
                case ")":
                    self.advance()
                    return Token(")", RIGHT_P)
                #return error if this is not an understood character
                case _ :
                    return self.error
                
        return Token(EOF, None)

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()


    def error(self):
        raise Exception("Invalid Syntax")

    def factor(self):
        '''
        factor  : INTEGER | ( INTEGER )
        '''
        token = self.current_token

        # INTEGER
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        # (INTEGER)
        elif self.current_token.type == LEFT_P:
            self.eat(LEFT_P)
            result = self.expr()
            self.eat(RIGHT_P)
            return result
    
    
    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.get_next_token()
        else:
            return self.error()
    
    def term(self):

        result = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            match token.type:
                case 'MUL':
                    self.eat(MUL)
                    result *= self.factor()
                case 'DIV':
                    self.eat(DIV)
                    result /= self.factor()
        return result
    
    

    def expr(self):
        result = self.term()

        while self.current_token.type in (MINUS, PLUS):
            token = self.current_token
            match token.type:
                case 'PLUS':
                    self.eat(PLUS)
                    result += self.term()
                case 'MINUS':
                    self.eat(MINUS)
                    result -= self.term()
        
        return result
    
    
             

def main():
    while True:
        try:
            # to run under python3 , replace 'raw input' call with 'input'
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.expr()
        print(result)

if __name__ == '__main__':
    main()