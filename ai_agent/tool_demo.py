import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from ai_agent.tools.calculator import calculator
from ai_agent.tools.image_generator import draw_image
from ai_agent.tools.code_interpreter import execute_python
from ai_agent.tools.stock_news import get_stock_news
from ai_agent.tools.utils.image_utils import setup_matplotlib
from ai_agent.config.settings import LLM_CONFIG
from ai_agent.prompts.tool_prompts import ToolPromptBuilder
from ai_agent.prompts.normal_prompts import *

def init_agent(system_prompt: str = None, use_python: bool = False) -> AgentExecutor:
    """初始化 ReAct Agent"""
    callbacks = [StreamingStdOutCallbackHandler()]

    # 直接在配置中添加callbacks
    llm = ChatOpenAI(**LLM_CONFIG, callbacks=callbacks)
    tools = [calculator, draw_image, execute_python,get_stock_news]

    prompt = PromptTemplate.from_template(
        ToolPromptBuilder.build_prompt(system_prompt, include_python_guidelines=use_python)
    )

    agent = create_react_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        callbacks=callbacks
    )


async def main():
    """主函数：初始化代理并处理查询"""
    setup_matplotlib()
    agent = init_agent(system_prompt=defaultTemplate(),use_python=True)

    while True:
        query = input("\n请输入您的问题（输入'quit'退出）: ").strip()
        if query.lower() == 'quit':
            break

        try:
            response = await agent.ainvoke({"input": query})
            output = response.get('output', response)
            print(f"\n最终结果: {output}")
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
