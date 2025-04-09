from RTEResult import RTEResult
from Errors import RunTimeError
from Token import *
#######################
#   VALUES
####################

class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self,context =None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multiply_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divide_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(other.pos_start, 
                other.pos_end, "Divison by zero",
                self.context)
            return Number(self.value / other.value).set_context(self.context), None
        
        
    def greater_than(self,other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        
    def greater_than_eq(self,other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        
    def less_than(self,other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        
    def less_than_eq(self,other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
    
    def equal_to(self,other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
    
    def anded_by(self,other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
    
    def ored_by(self,other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        
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
        if isinstance(other,Number):
            return Number(self.value ** other.value).set_context(self.context), None
    
    def __repr__(self):
        return str(self.value)
        
####################
#   SYMBOL TABLE
####################

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):                        # get value from certain variable name
        value = self.symbols.get(name,None)     # get name or default value of None
        if value == None and self.parent:       # If there's a value is None and theres a parent, return the global value
            return self.parent.get(name)
        return value                            # otherwise return the local value

    def set(self, name, value):
        self.symbols[name] = value
    
    def remove(self,name):
        del self.symbols[name]

#################
#   Interpreter
###################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}' # method name is set as the type of name]
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self,node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self,node, context):
        return RTEResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperatorNode(self,node, context):
        # after finding binary operator, needs to find left number node and right number node
        res = RTEResult()

        left = res.register(self.visit(node.left_node, context)) # get left node
        if res.error:
            return res
        
        right = res.register(self.visit(node.right_node, context)) # get right node
        if res.error:
            return res
        
        #Check binary node
        # This code is a bit weird, but it makes it cleaner; basically lamda function is used
        # to map token types to corresposonding binary_operator methods
        # Example: if token type is ADD, do left.added_to(right), a and b are variables for left and right
        binary_nodes = {TT_ADD: lambda a, b: a.added_to(b),
                        TT_SUBTRACT: lambda a, b: a.subbed_by(b),
                        TT_MULTIPLY: lambda a, b: a.multiply_by(b),
                        TT_DIVIDE: lambda a, b: a.divide_by(b),
                        TT_POWER: lambda a, b: a.power_by(b),

                        TT_GREATER_THAN: lambda a, b: a.greater_than(b),
                        TT_GREATER_THAN_EQUALS: lambda a,b: a.greater_than_eq(b),
                        TT_LESS_THAN: lambda a,b: a.less_than(b),
                        TT_LESS_THAN_EQUALS: lambda a, b: a.less_than_eq(b),
                        TT_EQUALS_TO: lambda a, b: a.equal_to(b),
                        (TT_KEYWORD, 'AND'): lambda a, b: a.anded(b),
                        (TT_KEYWORD, 'OR'):lambda a, b: a.ored(b)
                        }

        if (node.op_tok.type or (node.op_tok.type, node.op_tok.value)) in binary_nodes:
            result, error = binary_nodes[node.op_tok.type](left, right)
        

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self,node, context):
        res = RTEResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_SUBTRACT:
            number, error = number.multiply_by(Number(-1))
        if node.op_tok.matches(TT_KEYWORD, 'NOT'):
            number, error = number.notted()
        
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_VarAccessNode(self,node,context):
        res = RTEResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTEResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context)) # Get the variable value
        if res.error:return res

        context.symbol_table.set(var_name,value) # This sets a new symbol or variable within the symbol_table dictionary
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTEResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)
            

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)
        
        return res.success(None)
    
    def visit_ForNode(self, node, context):
        res = RTEResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res
        
        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        # Basically if we start from incrementing down or up
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.visit(node.body_node, context))
            if res.error: return res
        
        return res.success(None)




    def visit_WhileNode(self, node,context):
        pass



