
#Interpreter of simple arithmetic expressions

'''
token types

eof (end of file) token is used to indicated that
there is no more input left for lexical analysis

'''

INTEGER, PLUS, EOF, SUBTRACT, MULTIPLY, DIVIDE = 'INTEGER', 'PLUS', 'EOF', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'

class Token(object): # these are the possible values we want in a calculater, such as digits and operators
    def __init__(self,type,value):
        #types are EOF, INTEGER, and PLUS
        self.type = type
        # values are integer values, +, -,  or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS '+')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Interpreter(object):
    def __init__(self,text):
        #client string is 3 + 5
        self.text = text
        # index of string
        self.pos = 0
        #current token 
        self.current_token = None
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception("Error parsing input")

    def advance(self):
        # increments pos value by one and sets current_char variable
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char.isspace() is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    def get_next_token(self):

        # also called tokenizer or scanner
        # responsible for braking a sentence down to tokens, one at a time

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER,self.integer())
            
            if self.current_char == '*':
                self.advance()
                return Token(MULTIPLY, '*')
            elif self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/')
            elif self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            elif self.current_char == '-':
                self.advance()
                return Token(SUBTRACT, '-')    
            self.error()
        
        return Token(EOF,None)


    def eat(self, token_type):
        # comparing types of tokens, if they are the same as the argument passed, then it is eaten, used as a form of validation checking
        if self.current_token.type == token_type :
            self.current_token = self.get_next_token()
        else:
            self.error()

    def term(self):
        token = self.current_token
        self.eat(INTEGER)
        return token.value
    

    def expr(self):
        '''
        expr -> INTEGER PLUS INTEGER
        set current token to the first token taken from input
        '''
        

        self.current_token = self.get_next_token()

        result = self.term()

        while self.current_token.type in (PLUS, SUBTRACT, MULTIPLY, DIVIDE):
            token = self.current_token

            if token.type == PLUS:
                self.eat(PLUS)
                result += self.term()
            elif token.type  == SUBTRACT:
                self.eat(SUBTRACT)
                result -= self.term()
            elif token.type == MULTIPLY:
                self.eat(MULTIPLY)
                result = result * self.term()
            elif token.type == DIVIDE:
                self.eat(DIVIDE)
                result = result /self.term()
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
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)

if __name__ == '__main__':
    main()

    
            
        
            

