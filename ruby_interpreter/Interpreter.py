from RTEResult import RTEResult
from Errors import RunTimeError
from Token import *
from Context import Context
from SymbolTable import SymbolTable
from Value import *
    


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
    
    def visit_StringNode(self,node, context):
        return RTEResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperatorNode(self,node, context):
        # after finding binary operator, needs to find left number node and right number node
        res = RTEResult()

        left = res.register(self.visit(node.left_node, context)) # get left node
        if res.should_return(): return res
        
        right = res.register(self.visit(node.right_node, context)) # get right node
        if res.should_return(): return res
        
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
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self,node, context):
        res = RTEResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == TT_SUBTRACT:
            number, error = number.multiply_by(Number(-1))
        if node.op_tok.matches(TT_KEYWORD, 'NOT'):
            number, error = number.notted()
        
        if error:
            return res.failure(error)
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
        
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTEResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context)) # Get the variable value
        if res.should_return(): return res

        context.symbol_table.set(var_name,value) # This sets a new symbol or variable within the symbol_table dictionary
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTEResult()

        for condition, expr, return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                if return_null:
                    return res.success(Number.null)
                return res.success(expr_value)
            

        if node.else_case:
            expr, return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            if return_null: return res.success(Number.null)
            return res.success(else_value)
        
        return res.success(Number.null)
    
    def visit_ForNode(self, node, context):
        res = RTEResult()
        elements = []

        if node.start_value_node and node.end_value_node:
            start_value = res.register(self.visit(node.start_value_node, context))
            if res.should_return(): return res

            end_value = res.register(self.visit(node.end_value_node, context))
            if res.should_return(): return res
            
            if node.step_value_node:
                step_value = res.register(self.visit(node.step_value_node, context))
                if res.should_return(): return res
            else:
                step_value = Number(1)

            i = start_value.value

            if step_value.value >= 0:
                condition = lambda: i < end_value.value

            else:
                condition = lambda: i > end_value.value

            while condition():
                context.symbol_table.set(node.var_name_tok.value, Number(i))
                i += step_value.value

                value = res.register(self.visit(node.body_node, context))
                if res.should_return() and not res.loop_continue and not res.break_loop:
                    return res

                if res.loop_continue:
                    continue
                if res.break_loop:
                    break
                elements.append(value)
            
        elif node.iterable_node:
            iterable_value = res.register(self.visit(node.iterable_node, context))

            for item in iterable_value.elements:
                context.symbol_table.set(node.var_name_tok.value, item)
                value = res.register(self.visit(node.body_node, context))
                if res.should_return() and not res.loop_continue and not res.break_loop:
                    return res
                if res.loop_continue:
                    continue
                if res.break_loop:
                    break
                elements.append(value)

        if node.return_null: return res.success(Number.null)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node,context):
        res = RTEResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true(): break

            value = res.register(self.visit(node.body_node,context))
            if res.should_return() and not res.loop_continue and not res.break_loop:
                return res
            
            if res.loop_continue:
                continue
            if res.break_loop:
                break

            elements.append(value)

        
        if node.return_null: return res.success(Number.null)
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
    
    def visit_UntilNode(self, node,context):
        res = RTEResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if condition.is_true(): break # The until node is just a NOT while loop. 

            value = res.register(self.visit(node.body_node,context))
            if res.should_return() and not res.loop_continue and not res.break_loop:
                return res
            
            if res.loop_continue:
                continue
            if res.break_loop:
                break

            elements.append(value)

        
        if node.return_null: return res.success(Number.null)
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
    
    def visit_FunctionDefinitionNode(self, node, context):
        res = RTEResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None

        body_node =  node.body_node
        arg_names = [arg_names.value for arg_names in node.arg_name_toks] # list of names (Strings) in arg_name_toks
        func_value = Function(func_name,body_node, arg_names, node.auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok: # If the has a name, we want to add function name with function value
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTEResult()
        args = [] # List of arguments being passed into the node when function is called

        value_to_call = res.register(self.visit(node.node_to_call,context))
        if res.should_return(): return res

        value_to_call = value_to_call.copy().set_pos(node.pos_start,  node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        return res.success(return_value)
    
    def visit_ListNode(self, node, context):
        res = RTEResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res
        
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
    
    def visit_ReturnNode(self, node,context):
        res = RTEResult()

        if node.node_to_return: # There may not be a node to return
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null
        
        return res.success_return(value)
    
    def visit_ContinueNode(self, node,context):
        return RTEResult().success_continue()

    def visit_BreakNode(self, node,context):
        return RTEResult().success_break()