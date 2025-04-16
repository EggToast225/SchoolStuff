######################
#   RUNTIME RESULT
######################

class RTEResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_continue = False
        self.break_loop = False

    

    def register(self, res): # This method propagrates to other nodes, (passes along)
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_continue = res.loop_continue
        self.break_loop = res.break_loop
        return res.value
    
    def success(self, value): # stop the propagation when a node is successful
        self.reset() 
        self.value = value
        return self
    
    def success_return(self, value): # return function value
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self): # Continue loop
        self.reset()
        self.loop_continue = True
        return self
    
    def success_break(self): # Break loop
        self.reset()
        self.break_loop = True
        return self
    
    def failure(self, error):
        self.reset()
        self.error = error
        return self
    
    def should_return(self):
        return (
            self.error or
            self.func_return_value or
            self.loop_continue or
            self.break_loop
        )