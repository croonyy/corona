import traceback
import builtins
import re
import click


def locate_print(s, is_re=False):
    # 保存原始 print 函数
    builtins._original_print = builtins.print

    def debug_print(*args, **kwargs):
        # 获取调用栈信息
        stack = traceback.extract_stack()[-2]  # 获取调用 debug_print 的上一层

        # 使用原始 print 输出调试信息（避免递归）
        oprint = builtins.__dict__["_original_print"]  # 保存原始 print 的引用
        value = "".join([str(i) for i in args])
        oprint(*args, **kwargs)  # 输出原始内容
        if (not is_re and s in value) or (is_re and s and re.search(s, value)):
            # 黄色输出
            tag = click.style(f"print loc:", bold=True, fg=(255, 0, 0))
            oprint(
                f'{tag}File "{stack.filename}", line {stack.lineno}, in {stack.name}'
            )
            oprint(f"{stack.line}")

    # 替换内置的 print 函数
    builtins.print = debug_print


# 'filename', 'line', 'lineno', 'locals', 'name'