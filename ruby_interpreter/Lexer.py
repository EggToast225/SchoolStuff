from Position import Position
from Token import *
from Errors import IllegalCharError, ExpectedCharError
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

        single_char_tokens = {
        '+': TT_ADD,
        '-': TT_SUBTRACT,
        '/': TT_DIVIDE,
        '*': TT_MULTIPLY,
        '(': TT_LPAREN,
        ')': TT_RPAREN,
        '[': TT_LSQUARE,
        ']': TT_RSQUARE,
        '^': TT_POWER,
        '>': TT_GREATER_THAN,
        '<': TT_LESS_THAN,
        ',': TT_COMMA
        }
        
        comparison_tokens = {
            '!': TT_NE,
            '=': TT_EQ,
            '>': TT_GREATER_THAN,
            '<': TT_LESS_THAN
        }
        
        string_token = {
            '"': TT_STRING
        }

        line_characters = ';\n'
        comment_char = '#'

        while self.current_char != None:
            if self.current_char in ' \t': # If the current character is a space or tab, just skip it
                self.advance()
            elif self.current_char == comment_char:
                self.skip_comment()
            elif self.current_char in DIGITS: # If character is number
                tokens.append(self.make_numbers())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier()) # If character is an alphabetical symbol
            elif self.current_char in comparison_tokens: # If the character is a comparison symbol (!, >, <, =)
                compare_token, error = self.make_comparison(comparison_tokens)
                if error: return None, error
                tokens.append(compare_token)
            elif self.current_char in single_char_tokens:
                if self.current_char == '-':
                    tokens.append(self.make_minus_or_arrow()) # To differentiate '-' and '->'
                else:
                    tokens.append(Token(single_char_tokens[self.current_char],pos_start=self.pos,pos_end=self.pos))
                    self.advance()
            elif self.current_char in string_token: # If the character is '"'
                tokens.append(self.make_string())
            elif self.current_char in line_characters:
                tokens.append(Token(TT_NEWLINE, pos_start= self.pos, pos_end=self.pos))
                self.advance()

            # case of an unrecognized character
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'" ) # returns an empty list and error
            
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None # return tokens and no Errors
    
    # Determines if the number_str is a float or Integer by the number of dots. 
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS +'.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0: return Token(TT_INT, int(num_str), pos_start, self.pos)
        elif dot_count == 1: return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
    
    # Makes identifier
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and (self.current_char in LETTERS_DIGITS + '_'):
            id_str += self.current_char
            self.advance()
        
        if id_str in KEYWORDS: # if id_str is in KEYWORDS, it's a keyword, otherwise, it's an identifier
            tok_type = TT_KEYWORD
        else:
            tok_type = TT_IDENTIFIER
        
        return Token(tok_type, id_str, pos_start, self.pos)
    
    def make_comparison(self, comparison_tokens):
        double_char_tokens = {
            '!=': TT_NE,
            '==': TT_EQUALS_TO,
            '>=': TT_GREATER_THAN_EQUALS,
            '<=': TT_LESS_THAN_EQUALS
        }

        comparison_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and (self.current_char in comparison_tokens):
            comparison_str += self.current_char
            self.advance()

        if comparison_str in double_char_tokens:
            tok_type = double_char_tokens[comparison_str]
        elif comparison_str in comparison_tokens:
            if comparison_str == '!':
                return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")
            tok_type = comparison_tokens[comparison_str]
        
        
        return Token(tok_type, comparison_str, pos_start, self.pos),None
    
    def make_minus_or_arrow(self):
        tok_type = TT_SUBTRACT
        pos_start = self.pos.copy()

        self.advance()

        if self.current_char == '>':
            tok_type = TT_ARROW
            self.advance()
        
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_char = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_char):
            if escape_char:
                string += escape_characters.get(self.current_char, self.current_char) # will use second arg if not in dictionary
            else:
                if self.current_char == '\\': # If it's a backslash, escape next character
                    escape_char = True
                string += self.current_char
            self.advance()
            escape_char = False
        
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)
    
    def skip_comment(self): # Skips comment
        self.advance()

        while self.current_char != '\n': # If character isn't newline, just skip it
            self.advance()

        # Advance after newline
        self.advance()