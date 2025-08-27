import ast
import tokenize

from copy import copy
from Typhon import logger
from functools import wraps
from typing import Union, List
from random import randint, choice

def remove_duplicate(List) -> list:
    """
    Remove duplicate items in list
    """
    return list(set(List))


def unescape_double_backslash(string) -> str:
    """
    Unescape double backslashes in a string
    
    :param string: the string to unescape
    :return: the unescaped string
    """
    return string.replace('\\\\', '\\')

def generate_unicode_char():
    """
    Generate a random Unicode character.

    Returns:
        str: A random Unicode character.
    """
    val = randint(0x4E00, 0x9FBF)
    return chr(val)

def general_bypasser(func):
    """
    Decorator for general bypassers.
    """
    func._is_bypasser = True
    @wraps(func)
    def check(self, payload):
        for i in payload[1]:
            if i.__name__ == func.__name__:
                return None # Do not do the same bypass
        return func(self, payload[0])
    return check

def bypasser_not_work_with(bypasser_list: List[str]):
    """
    Decorator for bypassers which do not work with any other bypasser in the list.
    """
    def _(func):
        func._is_bypasser = True
        @wraps(func)
        def check(self, payload):
            for i in payload[1]:
                if i.__name__ == func.__name__:
                    return None # Do not do the same bypass
            for i in payload[1]:
                for j in bypasser_list:
                    if i.__name__ == j:
                        return None # Do not work with this
            return func(self, payload[0])
        return check
    return _


class BypassGenerator:
    def __init__(self, payload: str, allow_unicode_bypass: bool):
        """
        Initialize the bypass generator with a payload.
        
        Args:
            :param payload: The Python expression/statement to be transformed
            :param allow_unicode_bypass: if unicode bypasses are allowed.
        """
        self.payload = payload
        self.bypass_methods = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if getattr(method, '_is_bypasser', False):
                    self.bypass_methods.append(method)   
    
    def generate_bypasses(self):
        """
        Generate all possible bypass variants by applying each transformation method.
        
        Returns:
            list: List of unique transformed payloads
        """
        bypassed = [self.payload]
        # for method in self.bypass_methods:
        #     bypassed.append(method([self.payload, []]))
        
        from Typhon import search_depth # The maximum search depth for combined bypassing
        # Generate combinations of multiple bypasses
        combined = self.combine_bypasses([self.payload, []], self.payload, search_depth)
        bypassed.extend(combined)
        
        return remove_duplicate(bypassed)  # Remove duplicates
    
    def combine_bypasses(self, payload: List[str, list], initial_payload: str, depth: int):
        """
        Recursively combine multiple bypass methods for deeper obfuscation.
        
        Args:
            payload (list): Current list of [payload string, [bypass_method1, bypass_method2, ...]]
            depth (int): Recursion depth limit
            initial_payload (str): Initial payload
            
        Returns:
            list: Combined transformed payloads
        """
        if depth == 0:
            return [payload[0]]
        
        variants = []
        for method in self.bypass_methods:
            _ = []
            try:
                new_payload = method(payload)
            except SyntaxError: # from AST parsing
                logger.debug(f'Bypasser {method.__name__} failed to parse payload: {payload[0]}')
                continue
            if (new_payload == payload[0] 
                or new_payload is None 
                or new_payload in variants
                or new_payload == initial_payload): continue
            _ = copy(payload)
            _[1].append(method)
            variants.append(new_payload)
            variants.extend(self.combine_bypasses([new_payload, _[1]], initial_payload, depth-1))
        return variants
    
    # def attr_to_subscript(self, payload):
    #     """
    #     Convert attribute access (a.b) to subscript notation (a["b"]).
        
    #     Args:
    #         payload (str): Input payload
            
    #     Returns:
    #         str: Transformed payload
    #     """
    #     class Transformer(ast.NodeTransformer):
    #         def visit_Attribute(self, node):
    #             return ast.Subscript(
    #                 value=self.visit(node.value),
    #                 slice=ast.Constant(value=node.attr),
    #                 ctx=ast.Load()
    #             )
        
    #     tree = ast.parse(payload, mode='eval')
    #     new_tree = Transformer().visit(tree)
    #     return ast.unparse(new_tree)
    @general_bypasser
    def encode_string_hex(self, payload):
        """
        Encode strings using hex escapes.
        """
        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    hex_str = ''.join('\\' + f'x{ord(c):02x}' for c in node.value)
                    return ast.Constant(value=hex_str)
                return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return unescape_double_backslash(ast.unparse(new_tree))

    @general_bypasser
    def switch_quotes(self, payload):
        """
        Change " to ' and ' to "
        """
        output = ''
        for char in payload:
            if char == "'":
                output += '"'
            elif char == '"':
                output += "'"
            else:
                output += char
        return output

    # def encode_string_base64(self, payload):
    #     """
    #     Encode strings using base64 decoding.
        
    #     Args:
    #         payload (str): Input payload
            
    #     Returns:
    #         str: Transformed payload
    #     """
    #     class Transformer(ast.NodeTransformer):
    #         def visit_Constant(self, node):
    #             if isinstance(node.value, str):
    #                 encoded = base64.b64encode(node.value.encode()).decode()
    #                 return ast.Call(
    #                     func=ast.Attribute(
    #                         value=ast.Call(
    #                             func=ast.Name(id='base64.b64decode', ctx=ast.Load()),
    #                             args=[ast.Constant(value=encoded)],
    #                             keywords=[]
    #                         ),
    #                         attr='decode',
    #                         ctx=ast.Load()
    #                     ),
    #                     args=[],
    #                     keywords=[]
    #                 )
    #             return node
        
    #     tree = ast.parse(payload, mode='eval')
    #     new_tree = Transformer().visit(tree)
    #     return ast.unparse(new_tree)
    @bypasser_not_work_with(
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex', 'string_reversing'])
    def numbers_to_binary_base(self, payload):
        """
        Convert numbers to binary base (e.g., 42 → 0b101010).
        """
        placeholder = ''
        while placeholder in payload or placeholder == '':
            placeholder = str(randint(1000000, 9999999))

        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, int):
                    return ast.Constant(value=f'0b{placeholder}{bin(node.value)[2:]}{placeholder}')
                return node

        try:
            tree = ast.parse(payload, mode='eval')
            new_tree = Transformer().visit(tree)
            return ast.unparse(new_tree).replace(f'\'0b{placeholder}', '0b').replace(f'{placeholder}\'', '')
        except (SyntaxError, AttributeError):
            return payload

    @bypasser_not_work_with(
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex', 'string_reversing'])
    def numbers_to_oct_base(self, payload):
        """
        Convert numbers to oct base.
        """
        placeholder = ''
        while placeholder in payload or placeholder == '':
            placeholder = str(randint(1000000, 9999999))
            
        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, int):
                    return ast.Constant(value=f'0o{placeholder}{oct(node.value)[2:]}{placeholder}')
                return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return ast.unparse(new_tree).replace(f'\'0o{placeholder}', '0o').replace(f'{placeholder}\'', '')

    @bypasser_not_work_with(
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex', 'string_reversing'])
    def numbers_to_hex_base(self, payload):
        """
        Convert numbers to hex base.
        """
        placeholder = ''
        while placeholder in payload or placeholder == '':
            placeholder = str(randint(1000000, 9999999))
        
        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, int):
                    return ast.Constant(value=f'0x{placeholder}{hex(node.value)[2:]}{placeholder}')
                return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return ast.unparse(new_tree).replace(f'\'0x{placeholder}', '0x').replace(f'{placeholder}\'', '')

    @general_bypasser
    def obfuscate_func_call(self, payload):
        """
        Obfuscate function calls using lambda wrappers.
        """
        class Transformer(ast.NodeTransformer):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Lambda):
                    return node
                try:
                    return ast.Call(
                        func=ast.Lambda(
                            args=ast.arguments(
                                posonlyargs=[],
                                args=[ast.arg(arg='a'), ast.arg(arg='b')],
                                kwonlyargs=[],
                                kw_defaults=[],
                                defaults=[]
                            ),
                            body=ast.Call(
                                func=ast.Name(id='a', ctx=ast.Load()),
                                args=[ast.Name(id='b', ctx=ast.Load())],
                                keywords=[]
                            )
                        ),
                        args=[node.func, node.args[0]],
                        keywords=[]
                    )
                except IndexError:
                    return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return ast.unparse(new_tree)

    @bypasser_not_work_with(['string_reversing'])
    def string_slicing(self, payload):
        """
        Break strings into concatenated parts or use slicing.
        """
        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str) and len(node.value) > 1:
                    # Split into character concatenation
                    parts = [ast.Constant(value=c) for c in node.value]
                    new_node = parts[0]
                    for part in parts[1:]:
                        new_node = ast.BinOp(
                            left=new_node,
                            op=ast.Add(),
                            right=part
                        )
                    return new_node
                return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return ast.unparse(new_tree)

    @bypasser_not_work_with(['string_slicing'])
    def string_reversing(self, payload):
        """
        Reverse string.
        """
        class Transformer(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str) and len(node.value) > 1:
                    reversed_str = node.value[::-1]
                    slice_node = ast.Subscript(
                        value=ast.Constant(value=reversed_str),
                        slice=ast.Slice(
                            lower=None,
                            upper=None,
                            step=ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1))
                        ),
                        ctx=ast.Load()
                    )
                    return slice_node
                return node

        tree = ast.parse(payload, mode='eval')
        new_tree = Transformer().visit(tree)
        return ast.unparse(new_tree)

    @general_bypasser
    def replace_semicolon_newlines(self, payload: str) -> str:
        """
        Replace semicolons with newlines.
        
        Note: Might cause bug when replacing ; inside strings (or whatever).
        If yes, please report it and I'll try to fix it (I'm lazyyyyy now).
        PR welcome.
        """
        return payload.replace(';', '\n')
