# Typhon: Lets solve pyjail without brain

**大概得等到明年中旬完成，等发布时会新建一个仓库公开。本仓库将作为我个人的git仓库，发布在团队账号上供参考。**

听着，我已经受够那些愚蠢的CTF pyjail题目了——每次我都要浪费时间在又臭又长的黑名单和各种pyjail总结之间找哪个链子没被过滤，或者在命名空间里一个一个运行`dir()`去找能用的东西。这简直就是一种折磨。

所以这就是Typhon，一个致力于让你不需要脑子也能做pyjail的一把梭工具。

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
    banned_chr: list,
    banned_ast: list[ast.AST],
    banned_audithook: list[str],
    max_length: int,
    log_level: str) 
```

`cmd`: RCE所使用的bash command  
`local_scope`: 沙箱内的全局变量空间  
`banned_chr`: 禁止的字符  
`banned_ast`: 禁止的AST节点  
`banned_audithook`: 禁止的审计事件  
`max_length`: payload的最大长度  
`depth`: 最大递归深度（最多到10，再多估计也没用了）  
`log_level`: 输出级别（只支持`info`和`debug`，不建议更改）  

**Command Line Interface**

这部分不是本工具的重点，但是PR welcome. 

## Step by Step Tutorial

假设有如下题目：

```python
def safe_run(cmd):
    if len(cmd) > 30: return "Command too long"
    if any([i for i in ['builtins', 'os', 'exec'] if i in cmd]): return "WAF!"
    exec(cmd, {'__builtins__': None})

safe_run(input("Enter command: "))
```

**Step1. 分析waf**

首先，我们需要分析一下pyjail waf的功能（这可能是唯一需要大脑的地方）。

可以看出，上述题目的waf如下：

- 限制长度为30
- 在exec的命名空间里禁止没有__builtins__
- 禁止使用builtins, os, exec字符

**Step2. 将waf导入Typhon**

首先我们将exec行删除：

```python
def safe_run(cmd):
    if len(cmd) > 30: return "Command too long"

safe_run(input("Enter command: "))
```

然后，我们以Typhon对应的bypass函数替代exec行, **并在该行上方`import Typhon`**：

```python

def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE('cat /f*', local_scope={'__builtins__': None},
    banned_chr=['builtins', 'os', 'exec'],
    max_length=30)

safe_run()
```

**Step3. 运行**

运行你的题目程序，等待**Jail broken**的信息出现即可。

## Import Note

- 当题目没有指定local_scope时，请不要填写local_scope参数，**并使用动态加载来调用bypass函数。**

假设题目为：

```python
def safe_run(cmd):
    if len(cmd) > 30: return "Command too long"
    if any([i for i in ['builtins', 'os', 'exec'] if i in cmd]): return "WAF!"
    exec(cmd, {'__builtins__': None})

safe_run(input("Enter command: "))
```

我们一定要这样做：

```python

def safe_run(cmd):
    __import__('Typhon').bypassRCE('cat /f*',
    banned_chr=['builtins', 'os', 'exec'],
    max_length=30)

safe_run()
```

这样Typhon才能通过获取调用时上一帧的栈帧来获取local_scope。


## Best Practice

