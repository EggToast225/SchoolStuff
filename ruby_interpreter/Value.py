#######################
#   VALUES
####################

from Errors import RunTimeError
from RTEResult import RTEResult
from Context import Context
from SymbolTable import SymbolTable
import os

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
        return RunTimeError(
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
        elif isinstance(other,String):
            return String(op_func(self.value,other.value)).set_context(self.context), None
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

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
    
class String(Value):
    def __init__(self,value):
        super().__init__()
        self.value = value

    def added_to(self,other):
        if isinstance(other,String):
            return String(self.value + other.value).set_context(self.context), None
        return None, super().illegal_operation(other)

    def multiply_by(self,other):
        if isinstance(other,Number):
            return String(self.value * other.value).set_context(self.context), None
        return None, super().illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'{self.value}'

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self,other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def multiply_by(self,other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, super().illegal_operation(other)
    
    def subbed_by(self,other):
        if isinstance(other, List):
            new_list = self.copy()
            try:
                new_list.elements.pop(other)
                return new_list, None
            except:
                return None, RunTimeError(
                    other.pos_start, other.pos_end,
                    "Element at this index can not be removed, index is out of bounds",
                    self.context
                )
        else:
            return None,super().illegal_operation(other)
        
    def divide_by(self,other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RunTimeError(
                    other.pos_start, other.pos_end,
                    "Element at this index can not be retrieved, index is out of bounds",
                    self.context
                )
        else:
            return None,super().illegal_operation(other)
    
    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

###########################
#   Base Function Class
###########################

class BaseFunction(Value):
    def __init__(self,name):
        super().__init__()
        self.name = name or "<anonymous>"
    
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self,arg_names, args):
        res = RTEResult()

        if len(args) > len(arg_names):
            return res.failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        elif len(args) < len(arg_names):
            return res.failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too few args passed into {self}",
                self.context
            ))
        
        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)): # in the list of arg_name and args, get name and value
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx) # update value to execute context
            exec_ctx.symbol_table.set(arg_name,arg_value) # Add to context
    
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTEResult()
        res.register(self.check_args(arg_names, args))
        if res.error : return res

        self.populate_args(arg_names, args, exec_ctx)

        return res.success(None)

######################
#   Function Class
######################

class Function(BaseFunction):
    def __init__(self,name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return
    
    def execute(self,args):
        from Interpreter import Interpreter
        res = RTEResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        
        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res
        
        if self.auto_return: # Returns a value if there's no function
            return_value = value or res.func_return_value or Number.null
        else:
            return_value = None or res.func_return_value or Number.null 

        return res.success(return_value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self,name):
        super().__init__(name)

    def execute(self, args):
        res = RTEResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error: return res

        return_value = res.register(method(exec_ctx))
        if res.error: return res

        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f"<built-in function {self.name}>"
    
    # Prints a value
    def execute_print(self, exec_ctx):# symbol tables holds all args passed in
        print(str(exec_ctx.symbol_table.get('value')))
        return RTEResult().success(Number.null)
    execute_print.arg_names = ['value']
    
    # Returns the print value
    def execute_print_ret(self, exec_ctx):# symbol tables holds all args passed in, 
        return RTEResult.success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RTEResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again.")
        return RTEResult().success(Number(number))
    execute_input_int.arg_names = []

    # Clears terminal
    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name ==  'nt' else 'clear') # If windows os, use cls, otherwise, use clear
        return RTEResult().success(Number.null)
    execute_clear.arg_names = []

    # Checks to see if arg is a number
    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTEResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ['value']

    # Checks to see if arg is a string
    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTEResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ['value']

    # Checks to see if arg is a list
    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTEResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ['value']

    # Checks to see if arg is a function
    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTEResult().success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ['value']

    # Appends argument to a list
    def execute_append(self, exec_ctx):
        list = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list, List):
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "First argument must be a list",
                    exec_ctx
                ))
        list.elements.append(value)
        return RTEResult().success(Number.null)

    execute_append.arg_names = ['list', 'value']

    # Pops from a list with a provided index
    def execute_pop(self, exec_ctx):
        list = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list, List):
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "First argument must be a list",
                    exec_ctx
                ))
        if not isinstance(index, Number):
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "Index must be a integer",
                    exec_ctx
                ))
        
        try:
            element = list.elements.pop(index.value)
        except:
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "Index out of bounds",
                    exec_ctx
                ))
        return RTEResult().success(element)
    execute_pop.arg_names = ['list', 'index']

    # built in extend function
    def execute_extend(self,exec_ctx):
        list1 = exec_ctx.symbol_table.get("list1")
        list2 = exec_ctx.symbol_table.get("list2")
        
        if not isinstance(list1, List):
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "First argument must be a list",
                    exec_ctx
                ))
        if not isinstance(list2, List):
            return RTEResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end, 
                    "Second argument must be a list",
                    exec_ctx
                ))
        
        list1.elements.extend(list2.elements)
        return RTEResult().success(Number.null)
    execute_extend.arg_names = ["list1", 'list2']

    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTEResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"Argument must be a list",
                exec_ctx
            ))
        
        return RTEResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ["list"]

    # Execute Files
    def execute_run(self, exec_ctx):
        import main
        fn = exec_ctx.symbol_table.get("fn")
        if not isinstance(fn, String):
            return RTEResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "Argument must be sting",
                exec_ctx
                ))
        
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        fn = fn.value
        file_path = os.path.abspath(fn)
        
        try:
            with open(file_path, "r") as f:
                script = f.read()
        except Exception as e:
            return RTEResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"Failed to load script {fn}" + str(e),
                exec_ctx
            ))
        
        _, error = main.run(fn, script)

        if error:
            return RTEResult().failure(RunTimeError(
                    self.pos_start, self.pos_end,
                    f"Failed to finishing executing script {fn} \n" +
                    error.as_string(),
                    exec_ctx
                ))
        
        return RTEResult().success(Number.null)
    execute_run.arg_names = ["fn"]

# This creates a constant for the built-in function
BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction('extend')
BuiltInFunction.clear       = BuiltInFunction('clear')
BuiltInFunction.len         = BuiltInFunction('len')
BuiltInFunction.run         = BuiltInFunction('run')


