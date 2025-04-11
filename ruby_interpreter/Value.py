#######################
#   VALUES
####################


######################
#   Value Class
######################
class Value: # This class basically returns an error if there is an illegal operation
    def __init__(self):
        self.set_pos()
        self.set_context()
    
    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self

    def execute(self, args):
        return RTEResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None): # main point of this class
        if not other: other = self
        return RTEResult(
			self.pos_start, other.pos_end,
			'Illegal operation',
			self.context
		)

######################
#   Number Class
######################
class Number(Value):
    def __init__(self,value):
        super().__init__()
        self.value = value
    
    def _binary_op(self, other, op_func): # Checks to see if operation is between two numbers, then does a function, which is lambda.
        if isinstance(other,Number):
            return Number(op_func(self.value,other.value)).set_context(self.context), None
        return None, super().illegal_operation(other)   # Otherwise, operation is illegal
    
    def _comparison_op(self, other, op_func): # Checks to see if operation is between two numbers, then does a function, which is lambda.
        if isinstance(other,Number):
            return Number(int(op_func(self.value,other.value))).set_context(self.context), None
        return None, super().illegal_operation(other)   # Otherwise, operation is illegal

    def added_to(self, other):
        return self._binary_op(other, lambda a, b: a + b)
    
    def subbed_by(self, other):
        return self._binary_op(other, lambda a, b: a - b)
    
    def multiply_by(self, other):
        return self._binary_op(other, lambda a, b: a * b)
        
    def divide_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.pos_start,
                other.pos_end, "Divison by zero",
                self.context)
            return self._binary_op(other, lambda a, b: a / b)
        
    def greater_than(self,other):
        return self._comparison_op(other, lambda a, b: a > b)
    
    def greater_than_eq(self,other):
        return self._comparison_op(other, lambda a, b: a >= b)
    
    def less_than(self,other):
        return self._comparison_op(other, lambda a, b: a < b)
    
    def less_than_eq(self,other):
        return self._comparison_op(other, lambda a, b: a <= b)
    
    def equal_to(self,other):
        return self._comparison_op(other, lambda a, b: a == b)
    
    def anded_by(self,other):
        return self._comparison_op(other, lambda a, b: bool(a) and bool(b))
    
    def ored_by(self,other):
        return self._comparison_op(other, lambda a, b: bool(a) or bool(b))
    
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
        
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def is_true(self):
        return self.value != 0
    
    def power_by(self,other):
        return self._binary_op(other, lambda a, b: a ** b)
    
    def __repr__(self):
        return str(self.value)