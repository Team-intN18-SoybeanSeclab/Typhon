.. typhon documentation master file, created by
   sphinx-quickstart on Thu Oct  2 11:45:33 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Typhon: 最好的 CTF pyjail 沙箱逃逸自动化解题工具
============================================================

**本文档尚未完善**

``Typhon`` 是一款基于python3的开源工具，旨在为CTF选手提供方便的pyjail自动化解决工具。

你当前所阅读的是 ``Typhon`` 1.0.10 文档。此版本 ``Typhon`` 主要完善了在当前变量空间自动寻找利用链的功能，并实现了关于字符串黑名单和长度限制的绕过器。

未来， ``Typhon`` 会逐步实现针对 ``AST`` （抽象语法树）， ``audithook`` （审计钩子）黑名单的绕过功能，并提供多行的绕过策略，为CTF选手提供强大的pyjail自动化解题工具。

:download:`下载项目源码 <https://github.com/Team-intN18-SoybeanSeclab/Typhon/archive/refs/heads/main.zip>`

.. code-block:: python

   import Typhon, ast

   def main():
      Typhon.bypass_RCE(
         'pwn_the_world',
         local_scope = {'__builtins__' : {'hack_for': fun()}}
         banned_chr = 'welcome',
         banned_re = '*.to*.',
         banned_ast = [ast.Typhon],
         max_length = 1337,
      )

:download:`下载项目源码 <https://github.com/Team-intN18-SoybeanSeclab/Typhon/archive/refs/heads/main.zip>`

安装
------

.. code-block:: bash

   pip install typhonbreaker

索引
------

.. toctree::
   :maxdepth: 2

   USAGE
   EXAMPLE
   FAQ

链接
------

* `GitHub <https://github.com/Team-intN18-SoybeanSeclab/Typhon>`_
* `PyPi <https://pypi.org/project/typhonbreaker/>`_
* `Blog <https://www.cnblogs.com/LAMENTXU/articles/19101758>`_
* `Search Page <https://typhonbreaker.readthedocs.io/zh-cn/latest/search.html>`_