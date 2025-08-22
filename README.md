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

为了更加灵活，Typhon提供两套接口：

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

参数解析：

`cmd`: RCE所使用的bash command
`local_scope`: 沙箱内的全局变量空间  
`banned_chr`: 禁止的字符  
`banned_ast`: 禁止的AST节点  
`banned_audithook`: 禁止的审计事件  
`max_length`: payload的最大长度  
`depth`: 最大递归深度（最多到10，再多估计也没用了）  
`log_level`: 输出级别（只支持`info`和`debug`，不建议更改）  

**Command Line Interface**

```bash
python3 -m Typhon 
```

### Step by Step Tutorial


### Quick Example

