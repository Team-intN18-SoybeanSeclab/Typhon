# Typhon: Lets solve pyjail without brain

Simplified Chinese |[English](./README_ENG.md)

**This tool is currently in the PoC stage and does not have practical capabilities yet, nor has it been released on any platform (pip, github, etc.). However, since the basic functions have been implemented, we welcome everyone to try and provide feedback. Currently, you can try`bypassMAIN`Functions to experience the functions of this tool. At present, you can read[Proof of Concept](#proof-of-concept)Partly understand the core ideas of this tool. **

Listen, I've had enough of those stupid dumb dumb CTF pyjail topics - every time I'm wasting time finding which chain is not filtered between a stinky blacklist and various pyjail summary, or running one by one in the namespace`dir()`Find something that can be used. This is simply torture.

So this is Typhon, a shuttle tool dedicated to making pyjail without having to a brain.

**Please be sure to finish reading this readme before using the Typhon tool. **

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

- You can complete pyjail questions without a brain, take care of your brain cells and eyeballs
- Have thousands of gadgets and almost all mainstream bypass methods
- Supports multiple functions to achieve different functions, such as RCE`bypassRCE()`, for reading files`bypassRead()`etc.

## How to Use

### Install

Typhon has been released on pypi. You can use pip to install:

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
    print_all_payload: bool = False,
    log_level: str = 'INFO') 
```

`cmd`: bash command used by RCE
`local_scope`: Global variable space in the sandbox
`banned_chr`: Forbidden characters
`banned_ast`: Prohibited AST node
`banned_re`: Forbidden regular expression (list or string)
`max_length`: Maximum length of payload
`allow_unicode_bypass`: Whether to allow unicode to bypass
`print_all_payload`: Whether to print all payloads
`depth`: Maximum recursion depth (the default value is recommended)
`log_level`: Output level (only`info`and`debug`Meaningful, no change is recommended)

**Command Line Interface**

This part is not the focus of this tool, but PR welcome.

## Step by Step Tutorial

Suppose there is the following question:

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

**Step1. Analysis waf**

First, we need to analyze the functionality of pyjail waf (which is probably the only place where the brain is needed).

It can be seen that the waf of the above question is as follows:

- The maximum limit length is 100
- There is no exec namespace`__builtins__`
- No use`builtins`character
- Set regular expressions`'.*import.*'`Limitation conditions

**Step2. Import waf into Typhon**

First we delete the exec line:

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

Then, we replace the exec line with the bypass function corresponding to Typhon, import WAF at the corresponding position, ** and above the line`import Typhon`**：

```python
import re
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(cmd,
    banned_chr=['__builtins__'],
    banned_re='.*import.*',
    local_scope={'__builtins__': None},
    max_length=100)

safe_run(input("Enter command: "))
```

**Step3. Run**

Run your question program and wait for the **Jail broken** message to appear.

![image](./image/step-by-step-tutorial.png)

## Important Note

- Must make it`import Typhon`Put`Typhon`Built-in bypass the previous line of the function. otherwise,`Typhon`The current global variable space will not be available through the stack frame.

**Do:**
```python
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'])

safe_run('cat /f*')
```

**Don't:**
```python
import Typhon

def safe_run(cmd):
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'])

safe_run('cat /f*')
```

- Use the same python version as the title

There are some gadgets (such as inheritance chains) that search for corresponding object through indexes. The utilization of inheritance chains varies greatly with the index. Therefore, be sure to make sure that the running environment of Typhon is the same as the question.

**Not guaranteed? **

Yes, most questions won't give the corresponding python version. Therefore, **Typhon will prompt when using gadgets involving versions**.

In this case, CTF players often need to find the index value required by the gadgets in the question environment.

- Don't be in the same time`import`Used twice`Typhon`bypass function. If you have any requirements, please delete the existing ones`Typhon`modules and import them when needed.

**Do:**
```python
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'])
    del Typhon
    import Typhon
    Typhon.bypassRCE(cmd,
    local_scope={'__builtins__': None})

safe_run('cat /f*')
```

**Don't:**
```python
def safe_run(cmd):
    import Typhon
    Typhon.bypassRCE(cmd,
    banned_chr=['builtins', 'os', 'exec', 'import'])
    Typhon.bypassRCE(cmd,
    local_scope={'__builtins__': None})

safe_run('cat /f*')
```

- I can't use this payload, can I change it?

You can add the parameters`print_all_payload=True`, Typhon will print all the payloads it generates.

## Proof of Concept

This is how Typhon works:

### bypass by path & technique

We define two ways of bypass:

- path: Bypassed by different loads (e.g.`os.system('calc')`and`subprocess.Popen('calc')`）  
- technique: Use different techniques to process the same payload to bypass (e.g.`os.system('c'+'a'+'l'+'c')`and`os.system('clac'[::-1])`)  

Typhon has hundreds of built-in paths. Every time we want to bypass getting something, we first find all available through local_scope.`path`, Next, by`bypasser.py`Bypass method in generates each`path`Corresponding to different variants and try to bypass the blacklist.

### gadgets chain

This idea is[pyjailbreaker](https://github.com/jailctf/pyjailbreaker)Inspiration from tools.

pyjailbreaker does not directly implement RCE through gadgets in one step, but instead searches for the items needed in the RCE chain step by step. If the following blacklist exists:

- Local namespace no`__builtins__`
- No use`builtins`character

For this WAF, Typhon handles it like this:

- First, we pass`'J'.__class__.__class__`Get`type`
- Then we find the RCE chain that may be able to obtain builtins after obtaining the type`TYPE.__subclasses__(TYPE)[0].register.__globals__['__builtins__']`
- The blacklist of known topics has been filtered`__builtins__`Characters, then we put this path into bypasser to produce dozens of variants. Choose the shortest variant:`TYPE.__subclasses__(TYPE)[0].register.__globals__['__snitliub__'[::-1]]`
- Then we find the get``__builtins__``后的RCE链子`BUILTINS_SET['breakpoint']()`
- Finally, we will represent the placeholder for the builtins dictionary`BUILTINS_SET`Replace with the one obtained in the previous step`__builtins__`path, and so on`TYPE`Replace the placeholder with the real path and get the final payload.

```
'J'.__class__.__class__.__subclasses__('J'.__class__.__class__)[0].register.__globals__['__snitliub__'[::-1]]['breakpoint']()
```

### Step by Step

The order of workflow for Typhon is as follows:

- Each endpoint function (`bypassRCE`, `bypassREAD`, etc.) will call the main function`bypassMAIN`, the main function will collect all available gadgets as much as possible (as in the above example`type`) and pass the collected content to the corresponding subordinate function.
- `bypassMAIN`After the function simply analyzes the current variable space, it will:
  - Try to RCE directly (e.g.`help()`, `breakporint()`）
  - Try to get the generator
  - Try to get type
  - Try to get object
  - If the __builtins__ in the current space has not been deleted, but has been modified, try to restore (such as`id.__self__`）
  - If the __builtins__ in the current space is deleted, try to restore it from other namespaces
  - Inheriting, try to inherit the chain bypass
  - Ability to try to get import packages
  - Try to directly recover through the __builtins__ RCE
  - Pass the result to the lower function
- Get the lower function`bypassMAIN`After the result, the corresponding gadgets will be selected for processing according to the requirements implemented by the function (such as`bypassRCE`Focus on RCE,`bypassREAD`Focus on file reading,`bypassENV`Focus on reading environment variables). The process is similar to the above.

## Remaining Work to the first release

- [ ] Improve the end point function of bypass* (`bypassRCE`, `bypassREAD`, etc.)
- [ ] More gadgets
- [ ] More bypass methods

## Future Work

- [] Supports versions below python3.7
- [ ] Support audit hook bypass

## Contributors

**Author & Maintainer**

@ [LamentXU (Weilin Du)](https://github.com/LamentXU123)  

**Speical Thanks**

@ [hdsec](https://hdsec.cn)Give me the necessary encouragement
@ [jailctf](https://github.com/jailctf)The great Jailbreaker project inspired me

## License

This project is[Apache 2.0](https://github.com/LamentXU123/Typhon/blob/main/LICENSE)Release under the agreement.

Copyright (c) 2025 Weilin Du.

<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Team-intN18-SoybeanSeclab/Typhon&type=Date&theme=dark" />
<source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Team-intN18-SoybeanSeclab/Typhon&type=Date" />
<img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Team-intN18-SoybeanSeclab/Typhon&type=Date" />
</picture>

