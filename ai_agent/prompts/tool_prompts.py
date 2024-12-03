# prompts/tool_prompts.py
from typing import Optional


class ToolPromptBuilder:
    """工具提示词构建器"""

    BASE_FORMAT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

For simple questions that don't require tools({tools}), you can directly give the Final Answer.

Begin!

Question: {input}
{agent_scratchpad}"""

    PYTHON_GUIDELINES = """When using execute_python tools:
1. Always use complete and executable code
2. Include necessary imports
3. Use proper error handling
4. Format code blocks properly
5. Write code in multiple lines with proper line breaks
6. ALL FILES MUST be saved to 'output' directory
"""

    @classmethod
    def build_prompt(cls, system_prompt: Optional[str] = "你是一个智能助手，可以帮助用户解决各种问题。",
                     include_python_guidelines: bool = False) -> str:
        """
        构建提示词模板

        Args:
            system_prompt: 系统提示词
            include_python_guidelines: 是否包含Python指南
        """
        # 初始化最终提示词
        final_prompt = []

        # 如果需要包含Python指南，添加到最前面
        if include_python_guidelines:
            final_prompt.append(cls.PYTHON_GUIDELINES)

        # 添加系统提示词（如果有）
        if system_prompt:
            final_prompt.append(system_prompt)

        # 添加基础格式
        final_prompt.append(cls.BASE_FORMAT)

        # 用换行符连接所有部分
        return "\n\n".join(final_prompt)


class ToolPrompts:
    """预定义的工具提示词集合"""

    GENERAL_ASSISTANT = ToolPromptBuilder.build_prompt()  # 不需要传参数,使用默认值

    CODE_ASSISTANT = ToolPromptBuilder.build_prompt(
        """你是一个拥有使用Python运行能力的助手。
        """,
        include_python_guidelines=True  # 只在CODE_ASSISTANT中包含Python指南
    )

    DATA_ANALYST = ToolPromptBuilder.build_prompt(
        """你是一个数据分析助手。在分析数据时：
        1. 使用适当的数据可视化方法
        2. 提供清晰的分析解释
        3. 注意数据的准确性和可靠性
        """
    )
