# tools/code_interpreter.py

from typing import Optional
from langchain.tools import tool
from .utils.kernel_utils import KernelManager
import re

# 创建全局 KernelManager 实例
_kernel_manager = KernelManager()


def clean_code(code: str) -> str:
    """清理和格式化代码字符串"""
    # 移除代码块标记
    code = re.sub(r'^```\w*\n|^```|```$', '', code, flags=re.MULTILINE)

    # 清理空白行和首尾空格
    lines = [line.rstrip() for line in code.split('\n')]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # 检测并修正缩进
    if lines:
        # 找到第一个非空行的缩进级别
        first_indent = len(lines[0]) - len(lines[0].lstrip())
        if first_indent > 0:
            # 调整所有行的缩进
            lines = [line[first_indent:] if line.startswith(' ' * first_indent) else line
                     for line in lines]

    return '\n'.join(lines)


@tool
def execute_python(
        code: str,
        timeout: Optional[int] = 30
) -> str:
    """执行Python代码并返回结果。

    支持多行代码执行,可以进行数据分析、计算、绘图等操作。

    Args:
        code: 要执行的Python代码
        timeout: 超时时间(秒)

    示例:
    1. 简单计算: print(2 + 2)
    2. 数据处理:
       import pandas as pd
       df = pd.DataFrame({'a': [1,2,3]})
       print(df.describe())
    3. 绘图:
       import matplotlib.pyplot as plt
       plt.plot([1,2,3], [4,5,6])
       plt.show()
    """
    try:
        if not code:
            return '请提供要执行的Python代码'

        # 清理和格式化代码
        cleaned_code = clean_code(code)

        if not cleaned_code:
            return '清理后的代码为空，请检查输入'

        # 调试信息
        debug_info = f"准备执行的代码:\n{cleaned_code}\n{'=' * 50}\n"

        # 执行代码
        result = _kernel_manager.execute(cleaned_code, timeout=timeout)

        # 格式化输出
        if not result:
            return debug_info + "代码执行完成，无输出结果"
        return debug_info + result

    except Exception as e:
        error_msg = f"代码执行错误:\n{str(e)}\n\n原始代码:\n{code}\n\n清理后代码:\n{cleaned_code}"
        return error_msg


# 注册清理函数
import atexit


def cleanup():
    try:
        _kernel_manager.cleanup()
    except Exception as e:
        print(f"清理时发生错误: {e}")


atexit.register(cleanup)
