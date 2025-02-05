
#Interpreter of simple arithmetic expressions

'''
token types

eof (end of file) token is used to indicated that
there is no more input left for lexical analysis

'''

INTEGER, PLUS, EOF, SUBTRACT, MULTIPLY, DIVIDE, OPEN_PARAN, CLOSED_PARAN = ('INTEGER', 'PLUS', 'EOF', 'SUBTRACT','MULTIPLY',
                                                                            'DIVIDE', 'OPEN_PARAN', 'CLOSED_PARAN')

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

class Lexer(object):
    def __init__(self,text):
        #client string is 3 + 5
        self.text = text
        # index of string
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception("Invalid character")

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

            match self.current_char:
                case '*':
                    self.advance()
                    return Token(MULTIPLY, '*')
                case '/':
                    self.advance()
                    return Token(DIVIDE, '/')
                case '+':
                    self.advance()
                    return Token(PLUS, '+')
                case '-':
                    self.advance()
                    return Token(SUBTRACT, '-')
                case '(':
                    self.advance()
                    return Token(OPEN_PARAN, '(')
                case ')':
                    self.advance()
                    return Token(CLOSED_PARAN, ')') 
            self.error()
        
        return Token(EOF,None)
    

class Interpreter(object):
    def __init__(self,lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')
    
    def eat(self, token_type):
        # comparing types of tokens, if they are the same as the argument passed, then it is eaten, used as a form of validation checking
        if self.current_token.type == token_type :
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self):
        """Return an INTEGER token value.

        factor : INTEGER
        """
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif self.current_token.type == OPEN_PARAN:
            self.eat(OPEN_PARAN)
            result = self.expr()
            self.eat(CLOSED_PARAN)
            return result
        
            

    def term(self):
        '''
        term : factor ((MUL|DIV) factor)*
        '''
        result = self.factor()
        while self.current_token.type in (MULTIPLY, DIVIDE):
            token = self.current_token

            if token.type == MULTIPLY:
                self.eat(MULTIPLY)
                result *= self.factor()
            elif token.type == DIVIDE:
                self.eat(DIVIDE)
                result /= self.factor()
        
        return result

    def expr(self):
        '''
        Artihmetic expression parser / interpreter

        calc > 14 + 2 * 3 - 6 / 2
        17

        paran   : expr
        expr    : expr((PLUS|MINUS) term)*
        term    : ((MUL|DIV) factor)*
        factor  : INTEGER
       
        '''

        result = self.term()

        while self.current_token.type in (PLUS, SUBTRACT):
            token = self.current_token

            if token.type == PLUS:
                self.eat(PLUS)
                result += self.term()
            elif token.type  == SUBTRACT:
                self.eat(SUBTRACT)
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

    
            
        
            

