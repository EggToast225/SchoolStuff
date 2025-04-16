########################################
# PARSE RESULT
###################################

class ParseResult: # Class keeps track of Parse results and Nodes
    def __init__(self):
        self.node = None # Stores the Parsed Node
        self.error = None # Stores Errors
        self.advance_count = 0
        self.last_registered_count = 0
        self.to_reverse_count = 0
        
    def register_advancement(self):
        self.last_registered_count = 1
        self.advance_count +=1
    
    def is_valid(self):
        if self.error:
            return self
    

    #Tracks errors if there is an error
    def register(self, res):
        self.last_registered_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: # If there is an error in result
            self.error = res.error # Store the error in 'self.error'
        return res.node # Return the actual parsed node

    def success(self, node): # Stores the parsed node provided
        self.node = node
        return self
    
    def failure(self,error): # Used when an unexpected Error occurs; error will store IllegalCharError object
        if not self.error or self.last_registered_count == 0:
            self.error = error
        return self
    
    def try_register(self,res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)