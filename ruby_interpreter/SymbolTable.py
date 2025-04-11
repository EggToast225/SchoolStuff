####################
#   SYMBOL TABLE
####################

class SymbolTable:
    def __init__(self, parent = None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):                        # get value from certain variable name
        value = self.symbols.get(name,None)     # get name or default value of None
        if value == None and self.parent:       # If there's a value is None and theres a parent, return the global value
            return self.parent.get(name)
        return value                            # otherwise return the local value

    def set(self, name, value):
        self.symbols[name] = value
    
    def remove(self,name):
        del self.symbols[name]