###############
#   IMPORTS
###############
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
TT_ADD          = 'ADD'
TT_SUBTRACT     = 'SUBTRACT'
TT_MULTIPLY     = 'MULTIPLY'
TT_DIVIDE       = 'DIVIDE'
TT_EOF          = 'EOF'
TT_FLOAT        = 'FLOAT'
TT_INT          = 'INT'
TT_POWER        = 'POWER'
TT_LPAREN       = 'LPAREN'
TT_RPAREN       = 'RPAREN'

# Variables
TT_IDENTIFIER   = 'IDENTIFIER'
TT_KEYWORD      = 'KEYWORD'
TT_EQ           = 'EQ'

'''
    VAR          variable_name       =  <expr>
    ^                ^               ^
    KEYWORD      IDENTIFIER        EQUALS
'''
# Comparison Operators

TT_GREATER_THAN         = 'GT'
TT_LESS_THAN            = 'LT'
TT_EQUALS_TO            = 'EE'
TT_GREATER_THAN_EQUALS  = 'GTE'
TT_LESS_THAN_EQUALS     = 'LTE'
TT_NE                   = 'NE'


KEYWORDS = ['AND',
            'OR',
            'NOT',
            'IF',
            'THEN',
            'ELSIF',
            'ELSE',
            'WHILE',
            'FUNC',
            'FOR',
            'IN',
            'TO',
            'FUN',
            'STEP',
            'END',
            'RETURN',
            'CONTINUE',
            'BREAK',
            'DO',
            'UNTIL'
            ]

# Functions
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'

# Strings
TT_STRING = 'STRING'

# Lists
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'

# Line Tokens
TT_NEWLINE = 'NEWLINE'

# iteratable
TT_DOTDOT = 'DOTDOT'

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
    
    def matches(self, type_, value):
        return self.type == type_ and self.value.upper() == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

