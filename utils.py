import sys
import inspect
import builtins

from bypasser import *
from string import ascii_letters, digits
from types import FunctionType, ModuleType

def merge_dicts(dict1: dict, dict2: dict) -> dict:
    if type(dict1)!= dict:
        return dict2
    if type(dict2)!= dict:
        return dict1
    return {**dict1, **dict2}

def tag_variables(variables, change_in_builtins) -> list:
    """
    Tag each item in a variable namespace according to its type
    
    :param variables: The variable namespace to analyze (typically globals() or locals())
    :param change_in_builtins: The list of var changed included in __builtins__
    :return: Dictionary with tagging information
    """
    tagged = {}
    builtins_set = set(dir(builtins))
    
    for name, obj in variables.items():
        # Check if it's a builtin object
        if name in builtins_set:
            tagged[name] = 'BUILTINS'
            continue
        if isinstance(obj, dict) and set(obj.keys()) == set(dir(builtins)):
            if change_in_builtins:
                tagged[name] = 'BUILTINS_SET_CHANGED'
            else:
                tagged[name] = 'BUILTINS_SET'
            # Actually, BUILTINS_SET should be BUILTINS_DICT......
            # But fuck it, no one cares.
            continue
        # Check if it's a user-defined function
        if isinstance(obj, FunctionType) and obj.__module__ != 'builtins':
            # Check if it's a lambda function
            if obj.__name__ == '<lambda>':
                tagged[name] = 'USER_DEFINED_LAMBDA'
            else:
                tagged[name] = 'USER_DEFINED_FUNCTION'
            continue
        # Check if it's a module
        if isinstance(obj, ModuleType):
            tagged[name] = 'MODULE_{}'.format(obj.__name__.upper())
            continue
        # Check if it's a class
        if inspect.isclass(obj):
            tagged[name] = 'USER_DEFINED_CLASS_{}'.format(obj.__name__.upper())
            continue
        # Check for user-defined variables
        try:
            if hasattr(obj, '__name__'):
                obj_name = obj.__name__
            elif hasattr(obj, '__class__'):
                obj_name = obj.__class__.__name__
            else:
                obj_name = str(obj)
            # Sanitize object name (keep only alphanumeric, replace others with _)
            obj_name = ''.join(c if c.isalnum() else '_' for c in obj_name).upper()
            tagged[name] = 'USER_DEFINED_{}'.format(obj_name)
        except:
            tagged[name] = 'UNKNOWN'
    return tagged

def tag_scope(scope: dict, change_in_builtins: int) -> dict:
    """
    Tag each item in a scope (e.g. globals(), locals()) according to its type
    
    :param scope: The scope to analyze
    :param change_in_builtins: The list of var changed included in __builtins__
    :return: Dictionary with tagging information
    """
    return {k: [v, tag_variables({k: v}, change_in_builtins)[k]] for k, v in scope.items()}

def is_tag(string: str) -> bool:
    """
    Check if a string is a valid tag
    
    :param string: The string to check
    :return: True if the string is a valid tag, False otherwise
    """
    prefix = ('USER_DEFINED_', 'MODULE_')
    fixed_tag = ['BUILTINS_SET', 'BUILTINS_SET_CHANGED', 'BUILTINS', 'UNKNOWN']
    return (string.startswith(prefix) or string in fixed_tag)

def parse_payload_list(
    payload: list[str],
    char_blacklist: list[str],
    allow_unicode_bypass: bool,
    local_scope: dict,
    cmd = Union[str, None]) ->  list:
    """
    Parse a list of payloads (parse tags)

    :param payload: the payload to parse
    :param char_blacklist: the list of banned characters
    :param allow_unicode_bypass: if unicode bypasses are allowed.
    :param local_scope: the local scope to use for tag analysis
    :param cmd: the final RCE command to execute, default None
    :return: list of payloads
    """
    from Typhon import generated_path
    output = []
    allowed_letters = [i for i in ascii_letters + '_' if i not in char_blacklist and i not in local_scope]
    allowed_digits = [i for i in digits if i not in char_blacklist]
    payload_tag = ['RANDOMVARNAME', 'RANDOMSTRING', 'BUILTINOBJ', 'GENERATOR']
    builtin_obj = ['[]', '()', '{}'] # list, tuple, dict
    # builtin_obj.extend(allowed_digits)  # This line is only here to tell you that
    # digits do not work in some cases (like 1.__class__)
    builtin_obj.extend(["'" + i + "'" for i in allowed_letters])
    for path in payload:
        if 'RANDOMVARNAME' in path:
            if allowed_letters:
                output.append(path.replace('RANDOMVARNAME', allowed_letters[0]))
            # unicode bypass
            if allow_unicode_bypass:
                output.append(path.replace('RANDOMVARNAME', generate_unicode_char()))
            continue
        if 'RANDOMSTRING' in path:
            if allowed_letters:
                output.append(path.replace('RANDOMSTRING', '"'+allowed_letters[0]+'"'))
            # unicode bypass
            if allow_unicode_bypass:
                output.append(path.replace('RANDOMSTRING', '"'+generate_unicode_char()+'"'))
            continue
        if 'OBJ' in path: #TODO
            # if allowed_digits:
            #     output.append(path.replace('BUILTINOBJ', choice(allowed_digits)))
            # note: we assume that OBJ tag is in the beginning of the payload
            obj = path.split('.')[0] + '.' + path.split('.')[1]
            if allowed_letters:
                output.append(path.replace('OBJ', '"'+choice(allowed_letters)+'"'))
            # unicode bypass
            if allow_unicode_bypass:
                output.append(path.replace('OBJ', '"'+generate_unicode_char()+'"'))
            continue
        if 'GENERATOR' in path:
            if 'GENERATOR' in generated_path:
                output.append(path.replace('GENERATOR', generated_path['GENERATOR']))
            else:
                continue
        output.append(path)
    # if cmd != None: # Then we need to fill in the blanks with the RCE command
    #         CMD = "'" + cmd + "'"
    #         CMD_FILE = '"/bin/' + cmd.split(' ') + "'"
    #         CMD_UNFOLD_ARGS = ','.join() # TODO

    return output

def filter_path_list(path_list: list, tagged_scope: dict) -> list:
    """
    return a filtered list of payloads based on the scope
    
    :param path_list: list of payloads to filter
    :param scope: the scope to filter by
    :return: filtered list of payloads
    """
    def check_need(path: str, tagged_scope: dict, need: str) -> Union[str, None]:
        """
        Check if a path needs something in the scope
        
        :param path: the path to check
        :param scope: the scope to check in
        :return: the payload if the need is met, None otherwise
        """
        
        if need in sys.modules: # need is a module
            pass # TODO: check if module is already imported, if not, check if we can import modules
        elif need in dir(builtins): # need is a builtin
            need = __builtins__[need]
            for i in tagged_scope:
                if tagged_scope[i][0] == need:
                    return path
                elif 'BUILTINS_SET' in tagged_scope[i][1] and i != '__builtins__':
                    # If we successfully restore the builtins set, use it
                    return path.replace(need, i + '[' + need + ']')
                elif 'MOUDLE_BUILTINS' in tagged_scope[i][1]:
                        # If we successfully restore the builtins moudle, use it
                    return path.replace(need, i + '.' + need)
        elif is_tag(need): # need is a tag
            for i in tagged_scope:
                if tagged_scope[i][1] == need:
                    return path.replace(need, i)
        else: # need is a path
            pass # TODO
        return None
    filtered_list = []
    for path in path_list:
        path, need = path[0], path[1]
        if need: # we need something in this path
            need = need.split(',')
            for i in need:
                path = check_need(path, tagged_scope, i)
            if path:
                filtered_list.append(path)
        else: # we don't need anything in this path
            filtered_list.append(path)
    return filtered_list

def is_blacklisted(payload, banned_char, banned_AST, max_length) -> bool:
    """
    Check if a payload is blacklisted
    
    :param banned_chars: list of banned chars
    :param banned_AST: list of banned AST
    :param max_length: max length of the payload
    :return: True if the payload is blacklisted, False otherwise
    """
    ast_banned = False
    if max_length == None: length_check = False; max_length = 0
    else: length_check = True
    for bAST in banned_AST:
        if any(isinstance(node, bAST) for node in ast.walk(ast.parse(payload))):
            ast_banned = True
            break
    return (any(i in payload for i in banned_char) # banned character check
            or ast_banned # AST check
            or (len(payload) > max_length and length_check)) # max length check

def try_bypasses(pathlist,
                 banned_chars,
                 banned_AST,
                 max_length,
                 allow_unicode_bypass,
                 local_scope,
                 cmd=None) -> list:
    """
    Try to bypass each payload in the pathlist
    
    :param pathlist: list of payloads to try to bypass
    :param banned_chars: list of banned chars
    :param banned_AST: list of banned AST
    :param max_length: max length of the payload
    :param allow_unicode_bypass: if unicode bypasses are allowed.
    :param local_scope: the local scope to use for tag analysis
    :param cmd: command to RCE (in the final step, otherwise None)
    :return: list of successful payloads
    """
    successful_payloads = []
    pathlist = parse_payload_list(pathlist, banned_chars, allow_unicode_bypass, local_scope, cmd)
    Total = len(pathlist)
    for i, path in enumerate(pathlist):
        progress_bar(i+1, Total)
        # if not is_blacklisted(path, blacklist):
        #     successful_payloads.append(path)
        #     continue
        for _ in BypassGenerator(path, allow_unicode_bypass=allow_unicode_bypass).generate_bypasses():
            if not is_blacklisted(_, banned_chars, banned_AST, max_length): successful_payloads.append(_)
            continue
    sys.stdout.write('\n')
    successful_payloads.sort(key=len)
    return successful_payloads

def progress_bar(current, total, bar_length=80):
    """
    Progress bar function
    
    Note: sometime this may cause gliches in your console (somehow, idk).
    That's bad, but I don't want to rely on `tqdm` just for this simple feature.
    
    Not avaliable in debug mode
    """
    from Typhon import log_level_
    if log_level_ == 'DEBUG': return
    percent = float(current) * 100 / total
    arrow = '=' * int(percent / 100 * bar_length - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f"\rBypassing ({current}/{total}): [{arrow + spaces}] {percent:.1f}%")
    sys.stdout.flush()

def bypasses_output(bypassed_payload: str = ''):
    """
    Print a fancy output of the bypassed payload
    
    :param bypassed_payload: the bypassed payload
    :return: None
    """
    from Typhon import achivements
    print('\n')
    print('-----------Progress-----------')
    print('\n')
    for i in achivements:
        payload_len = achivements[i][1]
        if payload_len > 1:
            print('\033[34m' +  i + '(' + str(payload_len) + ' payloads found): \033[0m' + achivements[i][0])
        else: # only one payload or no payload found
            print('\033[34m' +  i + '(' + str(payload_len) + ' payload found): \033[0m' + achivements[i][0])
    print('\n')
    print('-----------Progress-----------')
    if bypassed_payload:
        print('\n')
        print('\033[36m+++++++++++Jail broken+++++++++++\033[0m')
        print('\n')
        print(bypassed_payload)
        print('\n')
        print('\033[36m+++++++++++Jail broken+++++++++++\033[0m')
    exit(0)