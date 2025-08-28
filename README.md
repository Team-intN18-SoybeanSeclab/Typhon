# Typhon: Lets solve pyjail without brain

**大概得等到明年中旬完成，等发布时会新建一个仓库公开。本仓库将作为我个人的git仓库，发布在团队账号上供参考。**

听着，我已经受够那些愚蠢的CTF pyjail题目了——每次我都要浪费时间在又臭又长的黑名单和各种pyjail总结之间找哪个链子没被过滤，或者在命名空间里一个一个运行`dir()`去找能用的东西。这简直就是一种折磨。

所以这就是Typhon，一个致力于让你不需要脑子也能做pyjail的一把梭工具。

```
    .-')          _           
   (`_^ (    .----`/          
    ` )  \_/`   __/     __,   
    __{   |`  __/      /_/       Typhon: a pyjail bypassing tool
   / _{    \__/ '--.  //      
   \_> \_\  >__/    \((       
        _/ /` _\_   |))       
```

## Highlights

- 不需要大脑就能完成pyjail题目，爱护您的脑细胞和眼球
- 拥有上千条gadgets和几乎所有主流的bypass方法
- 支持多种函数以达成不同功能，如RCE用`bypassRCE()`, 读文件用`bypassRead()`, 写文件用`bypassWrite()`等等

## How to Use

### Install

Typhon已经在pypi发布。你可以使用pip进行安装：

```
pip install TyphonBreaker
```

### Interface

**in Code**

```python
import Typhon
Typhon.bypassRCE(cmd: str,
    local_scope: Dict[str, Any],
    banned_chr: list = [],
    banned_ast: list[ast.AST] = [],
    banned_re: Union[str, list[str]] = [],
    allow_unicode_bypass = False,
    max_length: int = None,
    depth: int = 20,
    log_level: str = 'INFO') 
```

`cmd`: RCE所使用的bash command  
`local_scope`: 沙箱内的全局变量空间  
`banned_chr`: 禁止的字符  
`banned_ast`: 禁止的AST节点  
`banned_re`: 禁止的正则表达式（列表或字符串）  
`max_length`: payload的最大长度  
`allow_unicode_bypass`: 是否允许unicode绕过  
`depth`: 最大递归深度（建议使用默认值）  
`log_level`: 输出级别（只有`info`和`debug`有意义，不建议更改）  

**Command Line Interface**

这部分不是本工具的重点，但是PR welcome. 

## Step by Step Tutorial

假设有如下题目：

```python
import re
def safe_run(cmd):
    if len(cmd) > 100:
        return "Command too long"
    if any([i for i in ['import', '__builtins__'] if i in cmd]):
        return "WAF!"
    if re.match(r'.*import.*', cmd):
        return "WAF!"
    exec(cmd, {'__builtins__': {}})

safe_run(input("Enter command: "))
```

**Step1. 分析waf**

首先，我们需要分析一下pyjail waf的功能（这可能是唯一需要大脑的地方）。

可以看出，上述题目的waf如下：

- 限制长度最大值为100
- 在exec的命名空间里没有`__builtins__`
- 禁止使用`builtins`字符
- 设置了正则表达式`'.*import.*'`限制条件

**Step2. 将waf导入Typhon**

首先我们将exec行删除：

```python
import re
def safe_run(cmd):
    if len(cmd) > 100:
        return "Command too long"
    if any([i for i in ['import', '__builtins__'] if i in cmd]):
        return "WAF!"
    if re.match(r'.*import.*', cmd):
        return "WAF!"

safe_run(input("Enter command: "))
```

然后，我们以Typhon对应的bypass函数替代exec行，在对应位置导入WAF, **并在该行上方`import Typhon`**：

```python
import re
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(
    banned_chr=['__builtins__'],
    banned_re='.*import.*',
    local_scope={'__builtins__': None},
    max_length=100)

safe_run('whatever')
```

**Step3. 运行**

运行你的题目程序，等待**Jail broken**的信息出现即可。

![image](./image/step-by-step-tutorial.png)

## Important Note

- 一定要将行`import Typhon`放在`Typhon`内置绕过函数的上一行。否则，`Typhon`将无法通过栈帧获取当前的全局变量空间。

**Do:**
```python
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'], log_level='INFO')

safe_run('cat /f*')
```

**Don't:**
```python
import Typhon

def safe_run(cmd):
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'], log_level='INFO')

safe_run('cat /f*')
```


## Best Practice

## Maintainer

@ [LamentXU (Weilin Du)](https://github.com/LamentXU123)

## License

这个项目在[Apache 2.0](https://github.com/LamentXU123/Typhon/blob/main/LICENSE)协议下发布。

Copyright (c) 2025 Weilin Du.