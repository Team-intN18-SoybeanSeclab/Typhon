# Typhon: Lets solve pyjail without brain

**大概得等到明年中旬完成，等发布时会新建一个仓库公开。本仓库将作为我个人的git仓库，发布在团队账号上供参考。**

听着，我已经受够那些愚蠢的CTF pyjail题目了——每次我都要浪费时间在又臭又长的黑名单和各种pyjail总结之间找哪个链子没被过滤，或者在命名空间里一个一个运行`dir()`去找能用的东西。这简直就是一种折磨。

所以这就是Typhon，一个致力于让你不需要脑子也能做pyjail的一把梭工具。

## Highlights

- 不需要大脑就能完成pyjail题目，爱护您的脑细胞和眼球
- 拥有上千条gadgets和几乎所有主流的bypass方法
- 整个工具只有一个函数封装出去，上手极其简单（再次爱护您的脑细胞和眼球）

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
    local_scope: Dict[str, Any] = 
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
import subprocess

def save_run(cmd):
    if len(cmd) > 30: return "Command too long"
    exec(cmd, {'__builtins__': None})

save_run(input("Enter command: "))
```

**Step1. 分析waf**
首先，我们需要分析一下pyjail waf的功能（这可能是唯一需要大脑的地方）。

可以看出，上述题目的waf如下：

- 限制长度为30
- 在exec的命名空间里禁止没有__builtins__

**Step2. 将waf导入Typhon**

首先我们需要导入Typhon包：

```python
import Typhon
```

接下来，我们将exec行删除：

```python
import subprocess

def save_run(cmd):
    if len(cmd) > 30: return "Command too long"

save_run(input("Enter command: "))
```

最后，我们将Typhon.bypassRCE函数作为save_run的替代：

```python
import Typhon

def save_run(cmd):
    Typhon.bypassRCE('cat /f*', local_scope={'__builtins__': None}, banned_chr=[], banned_ast=[], banned_audithook=[], max_length=30, log_level='info')

save_run()
```

**Step3. 运行**

运行你的题目程序，等待**Jail broken**的信息出现即可。


## Best Practice

