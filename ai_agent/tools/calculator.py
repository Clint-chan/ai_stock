from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """计算数学表达式的结果。支持基本运算符 +,-,*,/"""
    try:
        expression = expression.strip('"\'').strip()
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算出错: {str(e)}"
