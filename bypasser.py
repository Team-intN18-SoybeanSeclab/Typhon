import ast

from Typhon import logger
from typing import Union, List
from copy import copy, deepcopy
from string import ascii_letters
from random import randint, choice
from functools import wraps, reduce

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
            if i == func.__name__:
                return None # Do not do the same bypass
        return func(self, payload[0]).replace(' + ', '+').replace(', ', ',')
    return check

def flatten_add_chain(n: ast.AST):
    parts = []
    def collect(x):
        if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Add):
            collect(x.left)
            collect(x.right)
        else:
            parts.append(x)
    collect(n)
    return parts

def bypasser_not_work_with(bypasser_list: List[str]):
    """
    Decorator for bypassers which do not work with any other bypasser in the list.
    """
    def _(func):
        func._is_bypasser = True
        @wraps(func)
        def check(self, payload):
            for i in payload[1]:
                if i == func.__name__:
                    return None # Do not do the same bypass
            for i in payload[1]:
                for j in bypasser_list:
                    if i == j:
                        return None # Do not work with this
            return func(self, payload[0]).replace(' + ', '+').replace(', ', ',')
        return check
    return _

def bypasser_must_work_with(bypasser_list: List[str]):
    """
    Decorator for bypassers which must work with at least one bypasser in the list.
    """
    def _(func):
        func._is_bypasser = True
        @wraps(func)
        def check(self, payload):
            for i in payload[1]:
                if i == func.__name__:
                    return None # Do not do the same bypass
            for j in bypasser_list:
                if not any(i == j for i in payload[1]):
                    return None # Do not work without this
            return func(self, payload[0]).replace(' + ', '+').replace(', ', ',')
        return check
    return _


class BypassGenerator:
    def __init__(self, payload: str, allow_unicode_bypass: bool, local_scope: dict, parent_payload: str = ''):
        """
        Initialize the bypass generator with a payload.
        
        Args:
            :param payload: The Python expression/statement to be transformed
            :param allow_unicode_bypass: if unicode bypasses are allowed
            :param local_scope: tagged local scope
            :param parent_payload: Parent payload of the payload
        """
        self.payload = payload
        self.allow_unicode_bypass = allow_unicode_bypass
        self.parent_payload = parent_payload
        self.local_scope = local_scope
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
        
        from Typhon import search_depth # The maximum search depth for combined bypassing
        # Generate combinations of multiple bypasses
        combined = self.combine_bypasses([self.payload, []], self.payload, search_depth)
        bypassed.extend(combined)
        bypassed = remove_duplicate(bypassed) # Remove duplicates
        # bypassed.sort(key=len)
        
        return bypassed
    
    def combine_bypasses(self, payload: List[Union[str, list]], initial_payload: str, depth: int):
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
            _ = deepcopy(payload)
            _[1].append(method.__name__)
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
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex'])
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
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex'])
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
        ['numbers_to_hex_base', 'numbers_to_oct_base', 'encode_string_hex'])
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

    # @general_bypasser
    # def obfuscate_func_call(self, payload):
    #     """
    #     Obfuscate function calls using lambda wrappers.
    #     """
    #     class Transformer(ast.NodeTransformer):
    #         def visit_Call(self, node):
    #             if isinstance(node.func, ast.Lambda):
    #                 return node
    #             try:
    #                 return ast.Call(
    #                     func=ast.Lambda(
    #                         args=ast.arguments(
    #                             posonlyargs=[],
    #                             args=[ast.arg(arg='a'), ast.arg(arg='b')],
    #                             kwonlyargs=[],
    #                             kw_defaults=[],
    #                             defaults=[]
    #                         ),
    #                         body=ast.Call(
    #                             func=ast.Name(id='a', ctx=ast.Load()),
    #                             args=[ast.Name(id='b', ctx=ast.Load())],
    #                             keywords=[]
    #                         )
    #                     ),
    #                     args=[node.func, node.args[0]],
    #                     keywords=[]
    #                 )
    #             except IndexError:
    #                 return node

    #     tree = ast.parse(payload, mode='eval')
    #     new_tree = Transformer().visit(tree)
    #     return ast.unparse(new_tree)

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
    
    @bypasser_must_work_with(['string_slicing'])
    def string_to_str_join(self, payload: str) -> str:
        """
        Convert string to string join.
        'a' + 'b' -> ''.join(['a', 'b'])
        """
        def is_str_like(n: ast.AST) -> bool:
            return (isinstance(n, ast.Constant) and isinstance(n.value, str)) or isinstance(n, ast.JoinedStr)

        class Transformer(ast.NodeTransformer):
            def visit_BinOp(self, node: ast.BinOp):
                if isinstance(node.op, ast.Add):
                    parts = flatten_add_chain(node)
                    if parts and all(is_str_like(p) for p in parts):
                        return ast.Call(
                            func=ast.Attribute(value=ast.Constant(value=''), attr='join', ctx=ast.Load()),
                            args=[ast.List(elts=parts, ctx=ast.Load())],
                            keywords=[]
                        )
                node.left = self.visit(node.left)
                node.right = self.visit(node.right)
                return node

        def _elem_src(n: ast.AST) -> str:
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                return repr(n.value)
            return ast.unparse(n)

        def _is_empty_str_join_call(n: ast.AST) -> bool:
            return (
                isinstance(n, ast.Call) and
                isinstance(n.func, ast.Attribute) and
                isinstance(n.func.value, ast.Constant) and n.func.value.value == '' and
                n.func.attr == 'join' and
                n.args and isinstance(n.args[0], ast.List)
            )

        def emit(n: ast.AST) -> str:
            if _is_empty_str_join_call(n):
                items = ','.join(_elem_src(e) for e in n.args[0].elts)
                return "''.join([" + items + "])"
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                return f"{emit(n.left)} + {emit(n.right)}"
            return ast.unparse(n)

        tree = ast.parse(payload, mode='eval')
        new_body = Transformer().visit(tree.body)
        ast.fix_missing_locations(new_body)
        return emit(new_body)

    @bypasser_must_work_with(['string_slicing'])
    def string_to_chr(self, payload: str) -> str:
        '''
        'a'+'b'+'c' -> chr(97)+chr(98)+chr(99)'
        '''
        from utils import find_object
        name = find_object(chr, self.local_scope)
        if name is None:
            return payload
            
        def is_single_char_str_const(n: ast.AST) -> bool:
            return isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) == 1

        def rebuild_plus_chain(nodes):
            return reduce(lambda l, r: ast.BinOp(left=l, op=ast.Add(), right=r), nodes)

        def _is_named_list_call(n: ast.AST, name: str) -> bool:
            return (isinstance(n, ast.Call) and
                    isinstance(n.func, ast.Name) and n.func.id == name and
                    n.args and isinstance(n.args[0], ast.List))

        def _emit_min_list(lst: ast.List) -> str:
            items = []
            for e in lst.elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, int):
                    items.append(str(e.value))
                else:
                    items.append(ast.unparse(e))
            return '[' + ','.join(items) + ']'

        def emit_min(n: ast.AST, name: str) -> str:
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                return emit_min(n.left) + '+' + emit_min(n.right)
            if _is_named_list_call(n, name):
                name = n.func.id
                arg0 = n.args[0]  # List
                return f"{name}(" + _emit_min_list(arg0) + ")"
            return ast.unparse(n)
        class Transformer(ast.NodeTransformer):
            def visit_BinOp(self, node: ast.BinOp):
                if isinstance(node.op, ast.Add):
                    parts = flatten_add_chain(node)
                    if parts and all(is_single_char_str_const(p) for p in parts):
                        calls = []
                        for p in parts:
                            code = ord(p.value)
                            call = ast.Call(
                                func=ast.Name(id=name, ctx=ast.Load()),
                                args=[ast.Constant(code)],
                                keywords=[]
                            )
                            calls.append(call)
                        return rebuild_plus_chain(calls)
                node.left = self.visit(node.left)
                node.right = self.visit(node.right)
                return node
        tree = ast.parse(payload, mode='eval')
        new_body = Transformer().visit(tree.body)
        ast.fix_missing_locations(new_body)
        return emit_min(new_body, name)

    @bypasser_must_work_with(['string_slicing'])
    def string_to_bytes(self, payload: str) -> str:
        '''
        'a'+'b'+'c' -> bytes([97])+bytes([98])+bytes([99])
        '''
        from utils import find_object
        name = find_object(bytes, self.local_scope)
        if name is None:
            return payload

        def is_single_char_str_const(n: ast.AST) -> bool:
            return isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) == 1

        def rebuild_plus_chain(nodes):
            return reduce(lambda l, r: ast.BinOp(left=l, op=ast.Add(), right=r), nodes)

        def _is_named_list_call(n: ast.AST, name: str) -> bool:
            return (isinstance(n, ast.Call) and
                    isinstance(n.func, ast.Name) and n.func.id == name and
                    n.args and isinstance(n.args[0], ast.List))

        def _emit_min_list(lst: ast.List) -> str:
            items = []
            for e in lst.elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, int):
                    items.append(str(e.value))
                else:
                    items.append(ast.unparse(e))
            return '[' + ','.join(items) + ']'

        def emit_min(n: ast.AST, name: str) -> str:
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                return emit_min(n.left) + '+' + emit_min(n.right)
            if _is_named_list_call(n, name):
                name = n.func.id
                arg0 = n.args[0]  # List
                return f"{name}(" + _emit_min_list(arg0) + ")"
            return ast.unparse(n)
        class Transformer(ast.NodeTransformer):
            def visit_BinOp(self, node: ast.BinOp):
                if isinstance(node.op, ast.Add):
                    parts = flatten_add_chain(node)
                    if parts and all(is_single_char_str_const(p) for p in parts):
                        calls = []
                        for p in parts:
                            code = ord(p.value)  # 单字符
                            call = ast.Call(
                                func=ast.Name(id=name, ctx=ast.Load()),
                                args=[ast.List(elts=[ast.Constant(code)], ctx=ast.Load())],
                                keywords=[]
                            )
                            calls.append(call)
                        return rebuild_plus_chain(calls)
                node.left = self.visit(node.left)
                node.right = self.visit(node.right)
                return node
        tree = ast.parse(payload, mode='eval')
        new_body = Transformer().visit(tree.body)
        ast.fix_missing_locations(new_body)
        return emit_min(new_body, name)
    
    def unicode_bypasses(self, payload: str, unicode_charset: str) -> str:
        """
        Bypass unicode encoding and decoding.
        abcdefghijklmnopqrstuvwxyz -> 𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻 (unicode_charset)
        """
        # Create mappings: regular -> unicode
        char_map = {}

        for regular, unicode_char in zip(ascii_letters, unicode_charset):
            char_map[regular] = unicode_char

        class Transformer(ast.NodeTransformer):
            """AST Node Transformer to replace non-string characters with Unicode equivalents"""
            
            def replace_chars(self, s):
                """Replace characters in a string using the char_map"""
                return ''.join([char_map[c] if c in char_map else c for c in s])
            
            def visit_Name(self, node):
                """Process variable/function names"""
                node.id = self.replace_chars(node.id)
                return self.generic_visit(node)
            
            def visit_Attribute(self, node):
                """Process attribute names (e.g., object.attribute)"""
                node.attr = self.replace_chars(node.attr)
                return self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                """Process function definitions (names only)"""
                node.name = self.replace_chars(node.name)
                return self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                """Process class definitions (names only)"""
                node.name = self.replace_chars(node.name)
                return self.generic_visit(node)
        tree = ast.parse(payload, mode='eval')
        new_body = Transformer().visit(tree.body)
        ast.fix_missing_locations(new_body)
        return ast.unparse(new_body).replace('__', '_＿')

    @bypasser_not_work_with(['unicode_replace_2'])
    def unicode_replace_1(self, payload: str) -> str:
        if self.allow_unicode_bypass:
            payload = self.unicode_bypasses(payload, '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵')
        return payload

    @bypasser_not_work_with(['unicode_replace_1'])
    def unicode_replace_2(self, payload: str) -> str:
        if self.allow_unicode_bypass:
            payload = self.unicode_bypasses(payload, '𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡')
        return payload